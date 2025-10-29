import os
import sys
import time
import json
import ctypes
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

import platform
import requests


def print_banner() -> None:
    """Prints an initial banner for the installer."""
    print("=== Git Installer - Instalador Automático ===")


def is_admin() -> bool:
    """Returns True if running with administrative privileges on Windows."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    except Exception:
        return False


def verify_windows() -> bool:
    """Checks whether the script is running on Windows."""
    return sys.platform == "win32"


def _resolve_latest_git_url(timeout: int = 15) -> Optional[str]:
    """Resolves the latest Git for Windows 64-bit installer download URL via GitHub API.

    Returns the asset URL for the 64-bit installer or None if it cannot be resolved.
    """
    api = "https://api.github.com/repos/git-for-windows/git/releases/latest"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "git-installer"}

    try:
        resp = requests.get(api, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            if name.endswith("-64-bit.exe") and name.startswith("Git-"):
                return asset.get("browser_download_url")
    except requests.RequestException:
        return None
    return None


def download_git(url: str, timeout: int = 300) -> Optional[Path]:
    """Downloads the Git installer from the given URL with retries and progress.

    Returns the path to the downloaded file or None on failure.
    """
    print(f"Baixando instalador do Git: {url}")
    target = Path(tempfile.gettempdir()) / "GitInstaller-setup.exe"

    backoffs = [2, 5, 10]
    for attempt in range(1, 4):
        print(f"[DOWNLOAD] tentativa {attempt}/3")
        # Remover artefato anterior (se existir) antes de cada tentativa
        try:
            if target.exists():
                target.unlink(missing_ok=True)  # type: ignore[call-arg]
        except Exception:
            pass

        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", 0))
                downloaded = 0
                chunk = 1024 * 64

                with open(target, "wb") as f:
                    start = time.time()
                    for part in r.iter_content(chunk_size=chunk):
                        if not part:
                            continue

                        # Checagem opcional de cancelamento via variável de ambiente
                        if os.environ.get("INSTALL_CANCELLED") == "1":
                            print("Download cancelado pelo usuário (variável INSTALL_CANCELLED=1).", flush=True)
                            try:
                                f.flush()
                            except Exception:
                                pass
                            try:
                                target.unlink(missing_ok=True)  # type: ignore[call-arg]
                            except Exception:
                                pass
                            return None

                        f.write(part)
                        downloaded += len(part)

                        if total > 0:
                            percent = downloaded / total
                            bar = int(percent * 30)
                            print(
                                f"[DOWNLOAD] [{'#' * bar}{'.' * (30 - bar)}] {percent:6.2%}",
                                flush=True,
                            )
                    elapsed = max(time.time() - start, 0.1)
                    speed = downloaded / elapsed / 1024
                    print(f"Download concluído ({downloaded/1024/1024:.2f} MB a {speed:.1f} KB/s)")

                if total and downloaded != total:
                    print("Aviso: tamanho baixado difere do esperado", flush=True)

            return target
        except requests.RequestException as e:
            print(f"Erro de rede ao baixar Git (tentativa {attempt}/3): {e}", flush=True)
        except OSError as e:
            print(f"Erro ao salvar arquivo do instalador (tentativa {attempt}/3): {e}", flush=True)

        # Backoff antes da próxima tentativa
        if attempt < 3:
            wait = backoffs[attempt - 1]
            print(f"Aguardando {wait}s para nova tentativa...", flush=True)
            try:
                time.sleep(wait)
            except KeyboardInterrupt:
                print("Cancelado pelo usuário durante o backoff.")
                return None

    print("Falha ao baixar o instalador do Git após 3 tentativas. Tente novamente mais tarde.")
    return None


def install_git(installer_path: Path, timeout: int = 1800) -> int:
    """Runs the Git installer silently. Returns the process return code."""
    log_path = Path(tempfile.gettempdir()) / "git_install.log"

    args = [
        str(installer_path),
        "/VERYSILENT",
        "/NORESTART",
        "/NOCANCEL",
        "/SP-",
        "/CLOSEAPPLICATIONS",
        "/RESTARTAPPLICATIONS",
        f"/LOG={log_path}",
    ]

    print("Iniciando instalação silenciosa do Git...")
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print(proc.stderr.strip())
        print(f"Log de instalação: {log_path}")
        return proc.returncode
    except subprocess.TimeoutExpired:
        print("Tempo limite excedido durante a instalação do Git", flush=True)
        return 1
    except OSError as e:
        print(f"Erro ao executar instalador: {e}", flush=True)
        return 1


def cleanup(path: Optional[Path]) -> None:
    """Removes a temporary file if it exists."""
    if not path:
        return
    try:
        if path.exists():
            path.unlink(missing_ok=True)  # type: ignore[call-arg]
    except Exception:
        pass


def main() -> int:
    """Main entry point for Git installer orchestration."""
    try:
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass

        print_banner()

        if not verify_windows():
            print("Este instalador suporta apenas Windows.")
            return 1

        if platform.machine().endswith("64") is False:
            print("Aviso: arquitetura não detectada como 64-bit.")

        if not is_admin():
            print("Executando sem privilégios de administrador (pode solicitar elevação).")

        print("Resolvendo URL do instalador mais recente do Git...")
        url = _resolve_latest_git_url() or ""
        if not url:
            print("Não foi possível resolver a URL do instalador do Git via API do GitHub.")
            print("Tente novamente mais tarde ou baixe manualmente de: https://gitforwindows.org/")
            return 1

        installer = download_git(url)
        if not installer:
            return 1

        code = install_git(installer)
        if code == 0:
            print("Git instalado com sucesso! ✅")
        else:
            print("Falha na instalação do Git. ❌")
        return code
    except KeyboardInterrupt:
        print("Instalação cancelada pelo usuário.")
        return 1
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return 1
    finally:
        # Deixar o arquivo para diagnóstico; comente a próxima linha caso prefira manter
        # cleanup(installer)
        pass


if __name__ == "__main__":
    sys.exit(main())
