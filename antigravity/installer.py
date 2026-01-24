#!/usr/bin/env python3
"""
Antigravity Installer (Gemini CLI)
Script Python que automatiza a instalação do Gemini CLI via npm.
"""

import sys
import os
import ctypes
import platform
from pathlib import Path

# Adicionar diretório raiz ao path para importar nodeecli
try:
    from nodeecli.modules.gemini_cli_installer import GeminiCliInstaller
    from nodeecli.modules.common import configure_stdout_stderr
except ModuleNotFoundError:
    try:
        project_root = Path(__file__).resolve().parent.parent
        if (project_root / 'nodeecli').is_dir() and str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from nodeecli.modules.gemini_cli_installer import GeminiCliInstaller
        from nodeecli.modules.common import configure_stdout_stderr
    except ModuleNotFoundError:
        print("Erro: Não foi possível importar os módulos necessários (nodeecli).")
        print("Execute este script a partir da raiz do projeto: python antigravity/installer.py")
        sys.exit(1)


def print_banner():
    """Exibe banner de boas-vindas."""
    print("=" * 60)
    print("    Antigravity Installer - Gemini CLI")
    print("    Instalação automatizada do @google/gemini-cli")
    print("=" * 60)
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


def main():
    """Função principal."""
    try:
        configure_stdout_stderr()
    except Exception:
        pass

    print_banner()

    # Verificar se está no Windows
    if not verify_windows():
        return 1

    # Verificar privilégios de administrador (recomendado para instalação global npm)
    admin_status = is_admin()
    if not admin_status:
        print("ℹ️  Nota: Executando sem privilégios de administrador.")
        print("   • A instalação global do npm geralmente requer administrador")
        print("   • Se falhar, tente executar novamente como administrador")
        print()
    else:
        print("✅ Executando com privilégios de administrador")
        print()

    try:
        # Instanciar e executar instalador
        installer = GeminiCliInstaller()
        success = installer.instalar()

        if success:
            print("\n🎉 Instalação do Antigravity (Gemini CLI) concluída com sucesso!")
            return 0
        else:
            print("\n❌ Falha na instalação do Antigravity.")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Instalação cancelada pelo usuário.")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
