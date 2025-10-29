import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Sequence


REPO_URL = "https://github.com/yzfly/mcp-excel-server"
INSTALL_DIR = Path("C:/Projetos")


def print_banner() -> None:
    """Exibe banner inicial do instalador MCP Excel Server."""
    print("=== MCP Excel Server - Instalador Automático ===")


def _run_streamed(cmd: Sequence[str], cwd: Optional[Path] = None) -> int:
    """Executa comando mostrando saída em tempo real, retornando o código."""
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        proc = subprocess.Popen(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creationflags,
        )
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                line = line.strip()
                if line:
                    print(line)
        return proc.wait()
    except FileNotFoundError:
        print(f"Comando não encontrado: {cmd[0]}")
        return 1
    except subprocess.SubprocessError as e:
        print(f"Erro ao executar comando: {e}")
        return 1


def verificar_git_instalado() -> bool:
    """Verifica se o Git está disponível no PATH."""
    if shutil.which("git"):
        return True
    try:
        return subprocess.run(["git", "--version"], capture_output=True).returncode == 0
    except Exception:
        return False


def verificar_python_instalado() -> bool:
    """Verifica se Python está disponível (usa o próprio interpretador em execução)."""
    try:
        print(f"Python detectado: {sys.version.split()[0]} ({sys.executable})")
        return True
    except Exception:
        return False


def verificar_uv_instalado() -> bool:
    """Verifica se 'uv' está instalado e no PATH."""
    return shutil.which("uv") is not None


def _is_cancelled() -> bool:
    """Retorna True se o usuário solicitou cancelamento via variável de ambiente."""
    return os.environ.get("INSTALL_CANCELLED") == "1"


def instalar_uv() -> bool:
    """Instala 'uv' via pip usando o Python corrente."""
    print("Instalando 'uv' via pip...")
    cmd = [sys.executable, "-m", "pip", "install", "-U", "uv"]
    rc = _run_streamed(cmd)
    if rc == 0:
        print("'uv' instalado com sucesso.")
        return True
    print("Falha ao instalar 'uv'.")
    return False


def garantir_diretorio_base() -> Path:
    """Garante que o diretório base de projetos exista."""
    try:
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Erro ao criar diretório {INSTALL_DIR}: {e}")
    return INSTALL_DIR


def criar_venv_uv(projeto_dir: Path) -> bool:
    """Cria ambiente virtual usando 'uv venv' dentro do diretório do projeto."""
    print("Criando ambiente virtual com 'uv venv'...")
    rc = _run_streamed(["uv", "venv"], cwd=projeto_dir)
    return rc == 0


def instalar_dependencias(projeto_dir: Path) -> bool:
    """Instala dependências do projeto com 'uv pip install -e .'"""
    print("Instalando dependências com 'uv pip install -e .'...")
    rc = _run_streamed(["uv", "pip", "install", "-e", "."], cwd=projeto_dir)
    return rc == 0


def preparar_repositorio(destino: Path) -> bool:
    """Garante que o repositório alvo exista e esteja sincronizado.

    - Se não existir: git clone.
    - Se existir e for clone do remoto esperado: fetch --all --prune + pull --ff-only.
    - Se existir e não corresponder ou não for Git: falha, a menos que MCP_EXCEL_FORCE_RECLONE=1
      (neste caso remove e reclona).
    """
    if not destino.exists():
        print(f"Clonando repositório para {destino}...")
        rc = _run_streamed(["git", "clone", REPO_URL, str(destino)])
        return rc == 0

    git_dir = destino / ".git"
    if git_dir.is_dir():
        try:
            res = subprocess.run(
                ["git", "-C", str(destino), "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            remote_url = (res.stdout or "").strip()
        except Exception as e:
            print(f"Falha ao obter remoto do repositório: {e}")
            return False

        if remote_url == REPO_URL:
            print("Diretório já contém o repositório correto; atualizando...")
            rc1 = _run_streamed(["git", "-C", str(destino), "fetch", "--all", "--prune"])
            if rc1 != 0:
                return False
            rc2 = _run_streamed(["git", "-C", str(destino), "pull", "--ff-only"])
            return rc2 == 0
        else:
            print(
                "Diretório existe mas não aponta para o repositório esperado.\n"
                f"Destino: {destino}\n"
                f"Origin atual: {remote_url}\n"
                f"Esperado: {REPO_URL}"
            )
            if os.environ.get("MCP_EXCEL_FORCE_RECLONE") == "1":
                print("Variável MCP_EXCEL_FORCE_RECLONE=1 ativa; removendo diretório para reclonar...")
                try:
                    shutil.rmtree(destino)
                except Exception as e:
                    print(f"Falha ao remover diretório existente: {e}")
                    return False
                print(f"Re-clonando repositório em {destino}...")
                rc = _run_streamed(["git", "clone", REPO_URL, str(destino)])
                return rc == 0
            else:
                print("Operação abortada: diretório existente não é o mcp-excel-server alvo.")
                return False
    else:
        print("Diretório de destino já existe mas não é um repositório Git válido.")
        if os.environ.get("MCP_EXCEL_FORCE_RECLONE") == "1":
            print("Variável MCP_EXCEL_FORCE_RECLONE=1 ativa; removendo diretório para reclonar...")
            try:
                shutil.rmtree(destino)
            except Exception as e:
                print(f"Falha ao remover diretório existente: {e}")
                return False
            print(f"Clonando repositório para {destino}...")
            rc = _run_streamed(["git", "clone", REPO_URL, str(destino)])
            return rc == 0
        else:
            print("Operação abortada: diretório existente não é um clone do mcp-excel-server.")
            return False


def main() -> int:
    """Fluxo principal do instalador MCP Excel Server."""
    # Import resiliente de configure_stdout_stderr (opcional)
    try:
        from nodeecli.modules.common import configure_stdout_stderr  # type: ignore
    except ImportError:
        try:
            project_root = Path(__file__).resolve().parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from nodeecli.modules.common import configure_stdout_stderr  # type: ignore
        except ImportError:
            def configure_stdout_stderr() -> None:  # type: ignore
                return None

    try:
        configure_stdout_stderr()
    except Exception:
        pass

    print_banner()

    if sys.platform != "win32":
        print("Este instalador suporta apenas Windows.")
        return 1

    # Pré-requisitos
    if not verificar_git_instalado():
        print("Git não encontrado no PATH. Instale o Git antes de continuar.")
        return 1
    if not verificar_python_instalado():
        print("Python não detectado.")
        return 1
    if not verificar_uv_instalado():
        if not instalar_uv():
            return 1

    base = garantir_diretorio_base()
    projeto = base / "mcp-excel-server"

    if not preparar_repositorio(projeto):
        print("Falha ao preparar o repositório (clone/atualização).")
        return 1

    if _is_cancelled():
        print("Instalação cancelada pelo usuário.")
        return 2

    if not criar_venv_uv(projeto):
        print("Falha ao criar ambiente virtual com 'uv'.")
        return 1

    if _is_cancelled():
        print("Instalação cancelada pelo usuário.")
        return 2

    if _is_cancelled():
        print("Instalação cancelada pelo usuário.")
        return 2

    if not instalar_dependencias(projeto):
        print("Falha ao instalar dependências do MCP Excel Server.")
        return 1

    # Verificação pós-instalação do ambiente virtual e Python
    if not verificar_instalacao(projeto):
        print("Falha na verificação pós-instalação do ambiente virtual.")
        return 1

    print("MCP Excel Server instalado com sucesso! ✅")
    return 0


def verificar_instalacao(projeto_dir: Path) -> bool:
    """Checa se o .venv existe e o Python do ambiente virtual é utilizável (Windows)."""
    venv_dir = projeto_dir / ".venv"
    if not venv_dir.is_dir():
        print("Verificação: diretório .venv não encontrado.")
        return False
    python_path = venv_dir / "Scripts" / "python.exe"
    if not python_path.exists():
        print("Verificação: python.exe não encontrado em .venv/Scripts.")
        return False
    rc = _run_streamed([str(python_path), "-c", "import sys; print(sys.version)"])
    if rc != 0:
        print("Verificação: falha ao executar Python do ambiente virtual.")
        return False
    print("Verificação pós-instalação concluída com sucesso.")
    return True


if __name__ == "__main__":
    sys.exit(main())
