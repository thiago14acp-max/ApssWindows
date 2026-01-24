#!/usr/bin/env python3
"""
VS Code Installer - Instalador Automático
Script Python que automatiza o download e instalação do Visual Studio Code no Windows 10/11
com todas as opções habilitadas automaticamente.
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



# Constantes
VSCODE_DOWNLOAD_URL = "https://update.code.visualstudio.com/latest/win32-x64-user/stable"
INSTALL_ARGS = ["/VERYSILENT", "/SP-", "/NORESTART", "/MERGETASKS=!runcode,desktopicon,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath"]


def print_banner():
    """Exibe banner de boas-vindas."""
    print("=" * 60)
    print("    VS Code Installer - Instalador Automático")
    print("     Download e instalação do VS Code no Windows")
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


def download_vscode():
    """
    Baixa o instalador do VS Code com barra de progresso.

    Returns:
        str: Caminho completo do arquivo baixado
        None: Em caso de erro
    """
    print("📥 Baixando VS Code...")
    print(f"   URL: {VSCODE_DOWNLOAD_URL}")
    print(f"   Tamanho estimado: ~100 MB")
    print()

    try:
        # Criar arquivo temporário com nome único
        temp_file = tempfile.NamedTemporaryFile(suffix='.exe', delete=False)
        installer_path = temp_file.name
        temp_file.close()  # Fechar pois vamos escrever diretamente no arquivo

        # Configurar timeout e tentativas
        TIMEOUT = (10, 120)  # connect, read
        response = None

        for attempt in range(3):
            try:
                print(f"   Tentativa {attempt + 1}/3...")
                response = requests.get(VSCODE_DOWNLOAD_URL, stream=True, timeout=TIMEOUT)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                print(f"   Erro na tentativa {attempt + 1}: {e}")
                if attempt == 2:
                    raise
                wait_time = 2 * (attempt + 1)
                print(f"   Aguardando {wait_time} segundos antes de tentar novamente...")
                time.sleep(wait_time)

        # Obter tamanho total do arquivo
        total_size = None
        total_mb = 0
        if response is not None:
            total_size = response.headers.get('Content-Length')
            if total_size is not None:
                total_size = int(total_size)
                total_mb = total_size / (1024 * 1024)
            else:
                total_size = None

        # Iniciar download com barra de progresso
        downloaded = 0
        chunk_size = 8192

        with open(installer_path, 'wb') as file:
            if response is not None:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        downloaded_mb = downloaded / (1024 * 1024)

                        # Exibir progresso
                        if total_size:
                            progress = downloaded / total_size * 100
                            # Barra de progresso com porcentagem e total
                            bar_length = 40
                            filled_length = int(bar_length * progress / 100)
                            bar = '█' * filled_length + '-' * (bar_length - filled_length)
                            print(f'\r   Progresso: |{bar}| {progress:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)', end='', flush=True)
                        else:
                            # Contador simples sem porcentagem
                            print(f'\r   Baixado: {downloaded_mb:.1f} MB', end='', flush=True)

        print()  # Nova linha após o progresso
        
        # Verificar integridade do download comparando bytes baixados com Content-Length
        if total_size is not None and downloaded != total_size:
            try:
                os.remove(installer_path)
            except Exception:
                pass
            print("\n❌ Download incompleto: tamanho inesperado do arquivo.")
            return None
            
        print(f"✅ Download concluído: {installer_path}")
        return str(installer_path)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erro de conexão após 3 tentativas: {e}")
        print("   Verifique sua conexão com a internet e tente novamente.")
        return None
    except IOError as e:
        print(f"\n❌ Erro ao salvar arquivo: {e}")
        print("   Verifique o espaço em disco e permissões.")
        return None
    except Exception as e:
        print(f"\n❌ Erro inesperado no download: {e}")
        return None


def install_vscode(installer_path):
    """
    Executa a instalação do VS Code com flags silenciosas.

    Args:
        installer_path (str): Caminho do instalador

    Returns:
        bool: True se instalação bem-sucedida, False caso contrário
    """
    print("\n🔧 Iniciando instalação do VS Code...")
    print("   Opções que serão habilitadas:")
    print("   ✅ Criar ícone na área de trabalho")
    print("   ✅ Adicionar ao menu de contexto (arquivos)")
    print("   ✅ Adicionar ao menu de contexto (pastas)")
    print("   ✅ Associar com tipos de arquivo suportados")
    print("   ✅ Adicionar ao PATH (comando 'code')")
    print()
    print("   ⏳ Isso pode levar alguns minutos...")
    print()

    try:
        # Verificar se o arquivo existe
        if not os.path.exists(installer_path):
            print(f"❌ Arquivo não encontrado: {installer_path}")
            return False

        # Construir comando em formato de lista
        log_file = Path(tempfile.gettempdir()) / "vscode_install.log"
        cmd = [str(installer_path), *INSTALL_ARGS, f"/LOG={log_file}"]
        
        # Opcional: imprimir comando efetivo para depuração quando modo verbose estiver ativado
        # print(f"Comando de instalação: {' '.join(cmd)}")

        # Executar instalação com codificação UTF-8
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

        # Verificar resultado
        if result.returncode == 0:
            print("✅ VS Code instalado com sucesso!")
            print()
            print("📋 Notas importantes:")
            print("   • O VS Code foi instalado no seu perfil de usuário")
            print("   • Reinicie o terminal para usar o comando 'code'")
            print("   • Para desinstalar, use o desinstalador padrão do Windows")
            print(f"   • Log da instalação salvo em: {log_file}")
            return True
        else:
            print(f"❌ Erro na instalação (código: {result.returncode})")
            if result.stderr:
                print(f"   Detalhes: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Erro durante a instalação: {e}")
        return False


def cleanup(installer_path):
    """
    Remove o arquivo do instalador após a instalação.

    Args:
        installer_path (str): Caminho do arquivo a ser removido
    """
    try:
        if os.path.exists(installer_path):
            os.remove(installer_path)
            print(f"🗑️  Arquivo temporário removido: {installer_path}")
    except Exception as e:
        print(f"⚠️  Não foi possível remover o arquivo temporário: {e}")


def main():
    """Função principal que orquestra o processo de instalação."""
    # Import resiliente de configure_stdout_stderr (opcional)
    try:
        from nodeecli.modules.common import configure_stdout_stderr  # type: ignore
    except ModuleNotFoundError:
        try:
            project_root = Path(__file__).resolve().parent.parent
            if (project_root / 'nodeecli').is_dir() and str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from nodeecli.modules.common import configure_stdout_stderr  # type: ignore
        except ModuleNotFoundError:
            def configure_stdout_stderr() -> None:  # type: ignore
                return None

    try:
        configure_stdout_stderr()
    except Exception:
        pass
    
    print_banner()

    # Verificar se está no Windows
    if not verify_windows():
        return 1
    
    # Verificar arquitetura do sistema
    arch = platform.machine().lower()
    if arch not in ("amd64", "x86_64"):
        print("⚠️  Aviso: Detectado sistema 32-bit.")
        print("   • Este script baixa o instalador 64-bit do VS Code")
        print("   • Para sistemas 32-bit, considere usar a variante win32-ia32")
        print("   • A instalação pode não funcionar corretamente")
        print()

    # Verificar privilégios de administrador
    admin_status = is_admin()
    if not admin_status:
        print("ℹ️  Nota: Executando sem privilégios de administrador.")
        print("   • O Instalador de Usuário do VS Code não requer administrador")
        print("   • Alguns ambientes corporativos podem solicitar elevação")
        print("   • Se encontrar problemas, execute como administrador")
        print()
    else:
        print("✅ Executando com privilégios de administrador")
        print()

    try:
        # Baixar o instalador
        installer_path = download_vscode()
        if not installer_path:
            return 1

        # Executar instalação
        success = install_vscode(installer_path)

        # Limpar arquivo temporário
        cleanup(installer_path)

        if success:
            print("\n🎉 Instalação concluída com sucesso!")
            print("   O VS Code está pronto para uso.")
            return 0
        else:
            print("\n❌ Falha na instalação.")
            print("   Tente executar o script novamente como administrador.")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Instalação cancelada pelo usuário.")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
