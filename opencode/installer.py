#!/usr/bin/env python3
"""
OpenCode Installer - Placeholder
Script Python que automatiza o download e instalação do OpenCode CLI.

ATENÇÃO: A URL de download é um placeholder e deve ser atualizada quando disponível.
"""

import os
import sys
import subprocess
import tempfile
import requests
import time
import ctypes
import platform
from pathlib import Path

# --- CONFIGURAÇÃO ---
# TODO: ATUALIZAR COM A URL REAL DO INSTALADOR DO OPENCODE
OPENCODE_DOWNLOAD_URL = "https://example.com/download/opencode-installer-win64.exe"
INSTALL_ARGS = ["/S"]  # Supondo instalação silenciosa padrão (/S, /VERYSILENT, etc.)
TIMEOUT = (10, 60)  # connect, read


def print_banner():
    """Exibe banner de boas-vindas."""
    print("=" * 60)
    print("    OpenCode CLI Installer")
    print("    Instalação automatizada do OpenCode CLI no Windows")
    print("=" * 60)
    print(f"⚠️  URL Configurada: {OPENCODE_DOWNLOAD_URL}")
    print()


def is_admin() -> bool:
    """Verifica se o script está sendo executado com privilégios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def verify_windows():
    """Verifica se está rodando no Windows."""
    if sys.platform != "win32":
        print("❌ Erro: Este script só funciona no Windows.")
        return False
    return True


def download_opencode():
    """Baixa o instalador do OpenCode."""
    print("📥 Iniciando download do OpenCode...")
    print(f"   URL: {OPENCODE_DOWNLOAD_URL}")

    # Verificar se é URL de placeholder
    if "example.com" in OPENCODE_DOWNLOAD_URL:
        print("\n⚠️  AVISO: URL de placeholder detectada.")
        print("   O download falhará propositalmente ou baixará um arquivo inválido.")
        print("   Atualize a variável OPENCODE_DOWNLOAD_URL no script.")
        # Simula delay de download
        time.sleep(1)
        return None

    try:
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        installer_path = temp_file.name
        temp_file.close()

        print("   Conectando...")
        response = requests.get(OPENCODE_DOWNLOAD_URL, stream=True, timeout=TIMEOUT)
        response.raise_for_status()

        total_size = int(response.headers.get('Content-Length', 0))
        downloaded = 0
        chunk_size = 8192

        print(f"   Salvando em: {installer_path}")
        with open(installer_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    # Lógica de barra de progresso simples poderia entrar aqui

        print("✅ Download concluído.")
        return installer_path

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro no download: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return None


def install_opencode(installer_path):
    """Executa o instalador baixado."""
    print("\n🛠️  Instalando OpenCode...")
    
    if not os.path.exists(installer_path):
        print("❌ Arquivo instalador não encontrado.")
        return False

    cmd = [installer_path] + INSTALL_ARGS
    print(f"   Executando: {' '.join(cmd)}")

    try:
        # Execução síncrona
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Instalação executada com sucesso!")
            return True
        else:
            print(f"❌ Falha na instalação (Código {result.returncode})")
            if result.stderr:
                print(f"   Erro: {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"❌ Erro ao executar instalador: {e}")
        return False


def cleanup(installer_path):
    """Remove arquivo temporário."""
    if installer_path and os.path.exists(installer_path):
        try:
            os.remove(installer_path)
            # print(f"🧹 Limpeza: {installer_path} removido.")
        except Exception:
            pass


def main():
    print_banner()

    if not verify_windows():
        return 1

    if not is_admin():
        print("ℹ️  Nota: Executando sem privilégios de administrador.")
        print("   Recomendado executar como Administrador para instalação correta.")
        print()

    installer_path = download_opencode()
    
    if not installer_path:
        print("\n❌ Processo abortado: Falha no download (ou URL placeholder).")
        print("   Edite o arquivo 'opencode/installer.py' com a URL correta.")
        return 1

    success = install_opencode(installer_path)
    cleanup(installer_path)

    if success:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
