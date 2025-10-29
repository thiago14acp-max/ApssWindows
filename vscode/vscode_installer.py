#!/usr/bin/env python3
"""
VS Code Installer - Instalador AutomÃƒÂ¡tico
Script Python que automatiza o download e instalaÃƒÂ§ÃƒÂ£o do Visual Studio Code no Windows 10/11
com todas as opÃƒÂ§ÃƒÂµes habilitadas automaticamente.
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
    print("    VS Code Installer - Instalador AutomÃƒÂ¡tico")
    print("     Download e instalaÃƒÂ§ÃƒÂ£o do VS Code no Windows")
    print("=" * 60)
    print()


def is_admin() -> bool:
    """Verifica se o script estÃƒÂ¡ sendo executado com privilÃƒÂ©gios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def verify_windows():
    """Verifica se estÃƒÂ¡ rodando no Windows."""
    if sys.platform != "win32":
        print("Ã¢ÂÅ’ Erro: Este script sÃƒÂ³ funciona no Windows.")
        return False
    return True


def download_vscode():
    """
    Baixa o instalador do VS Code com barra de progresso.

    Returns:
        str: Caminho completo do arquivo baixado
        None: Em caso de erro
    """
    print("Ã°Å¸â€œÂ¥ Baixando VS Code...")
    print(f"   URL: {VSCODE_DOWNLOAD_URL}")
    print(f"   Tamanho estimado: ~100 MB")
    print()

    try:
        # Criar arquivo temporÃƒÂ¡rio com nome ÃƒÂºnico
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
                            bar = 'Ã¢â€“Ë†' * filled_length + '-' * (bar_length - filled_length)
                            print(f'\r   Progresso: |{bar}| {progress:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)', end='', flush=True)
                        else:
                            # Contador simples sem porcentagem
                            print(f'\r   Baixado: {downloaded_mb:.1f} MB', end='', flush=True)

        print()  # Nova linha apÃƒÂ³s o progresso
        
        # Verificar integridade do download comparando bytes baixados com Content-Length
        if total_size is not None and downloaded != total_size:
            try:
                os.remove(installer_path)
            except Exception:
                pass
            print("\nÃ¢ÂÅ’ Download incompleto: tamanho inesperado do arquivo.")
            return None
            
        print(f"Ã¢Å“â€¦ Download concluÃƒÂ­do: {installer_path}")
        return str(installer_path)

    except requests.exceptions.RequestException as e:
        print(f"\nÃ¢ÂÅ’ Erro de conexÃƒÂ£o apÃƒÂ³s 3 tentativas: {e}")
        print("   Verifique sua conexÃƒÂ£o com a internet e tente novamente.")
        return None
    except IOError as e:
        print(f"\nÃ¢ÂÅ’ Erro ao salvar arquivo: {e}")
        print("   Verifique o espaÃƒÂ§o em disco e permissÃƒÂµes.")
        return None
    except Exception as e:
        print(f"\nÃ¢ÂÅ’ Erro inesperado no download: {e}")
        return None


def install_vscode(installer_path):
    """
    Executa a instalaÃƒÂ§ÃƒÂ£o do VS Code com flags silenciosas.

    Args:
        installer_path (str): Caminho do instalador

    Returns:
        bool: True se instalaÃƒÂ§ÃƒÂ£o bem-sucedida, False caso contrÃƒÂ¡rio
    """
    print("\nÃ°Å¸â€Â§ Iniciando instalaÃƒÂ§ÃƒÂ£o do VS Code...")
    print("   OpÃƒÂ§ÃƒÂµes que serÃƒÂ£o habilitadas:")
    print("   Ã¢Å“â€¦ Criar ÃƒÂ­cone na ÃƒÂ¡rea de trabalho")
    print("   Ã¢Å“â€¦ Adicionar ao menu de contexto (arquivos)")
    print("   Ã¢Å“â€¦ Adicionar ao menu de contexto (pastas)")
    print("   Ã¢Å“â€¦ Associar com tipos de arquivo suportados")
    print("   Ã¢Å“â€¦ Adicionar ao PATH (comando 'code')")
    print()
    print("   Ã¢ÂÂ³ Isso pode levar alguns minutos...")
    print()

    try:
        # Verificar se o arquivo existe
        if not os.path.exists(installer_path):
            print(f"Ã¢ÂÅ’ Arquivo nÃƒÂ£o encontrado: {installer_path}")
            return False

        # Construir comando em formato de lista
        log_file = Path(tempfile.gettempdir()) / "vscode_install.log"
        cmd = [str(installer_path), *INSTALL_ARGS, f"/LOG={log_file}"]
        
        # Opcional: imprimir comando efetivo para depuraÃƒÂ§ÃƒÂ£o quando modo verbose estiver ativado
        # print(f"Comando de instalaÃƒÂ§ÃƒÂ£o: {' '.join(cmd)}")

        # Executar instalaÃƒÂ§ÃƒÂ£o com codificaÃƒÂ§ÃƒÂ£o UTF-8
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

        # Verificar resultado
        if result.returncode == 0:
            print("Ã¢Å“â€¦ VS Code instalado com sucesso!")
            print()
            print("Ã°Å¸â€œâ€¹ Notas importantes:")
            print("   Ã¢â‚¬Â¢ O VS Code foi instalado no seu perfil de usuÃƒÂ¡rio")
            print("   Ã¢â‚¬Â¢ Reinicie o terminal para usar o comando 'code'")
            print("   Ã¢â‚¬Â¢ Para desinstalar, use o desinstalador padrÃƒÂ£o do Windows")
            print(f"   Ã¢â‚¬Â¢ Log da instalaÃƒÂ§ÃƒÂ£o salvo em: {log_file}")
            return True
        else:
            print(f"Ã¢ÂÅ’ Erro na instalaÃƒÂ§ÃƒÂ£o (cÃƒÂ³digo: {result.returncode})")
            if result.stderr:
                print(f"   Detalhes: {result.stderr}")
            return False

    except Exception as e:
        print(f"Ã¢ÂÅ’ Erro durante a instalaÃƒÂ§ÃƒÂ£o: {e}")
        return False


def cleanup(installer_path):
    """
    Remove o arquivo do instalador apÃƒÂ³s a instalaÃƒÂ§ÃƒÂ£o.

    Args:
        installer_path (str): Caminho do arquivo a ser removido
    """
    try:
        if os.path.exists(installer_path):
            os.remove(installer_path)
            print(f"Ã°Å¸â€”â€˜Ã¯Â¸Â  Arquivo temporÃƒÂ¡rio removido: {installer_path}")
    except Exception as e:
        print(f"Ã¢Å¡Â Ã¯Â¸Â  NÃƒÂ£o foi possÃƒÂ­vel remover o arquivo temporÃƒÂ¡rio: {e}")


def main():
    """FunÃ§Ã£o principal que orquestra o processo de instalaÃ§Ã£o."""
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

    # Verificar se estÃƒÂ¡ no Windows
    if not verify_windows():
        return 1
    
    # Verificar arquitetura do sistema
    arch = platform.machine().lower()
    if arch not in ("amd64", "x86_64"):
        print("Ã¢Å¡Â Ã¯Â¸Â  Aviso: Detectado sistema 32-bit.")
        print("   Ã¢â‚¬Â¢ Este script baixa o instalador 64-bit do VS Code")
        print("   Ã¢â‚¬Â¢ Para sistemas 32-bit, considere usar a variante win32-ia32")
        print("   Ã¢â‚¬Â¢ A instalaÃƒÂ§ÃƒÂ£o pode nÃƒÂ£o funcionar corretamente")
        print()

    # Verificar privilÃƒÂ©gios de administrador
    admin_status = is_admin()
    if not admin_status:
        print("Ã¢â€žÂ¹Ã¯Â¸Â  Nota: Executando sem privilÃƒÂ©gios de administrador.")
        print("   Ã¢â‚¬Â¢ O Instalador de UsuÃƒÂ¡rio do VS Code nÃƒÂ£o requer administrador")
        print("   Ã¢â‚¬Â¢ Alguns ambientes corporativos podem solicitar elevaÃƒÂ§ÃƒÂ£o")
        print("   Ã¢â‚¬Â¢ Se encontrar problemas, execute como administrador")
        print()
    else:
        print("Ã¢Å“â€¦ Executando com privilÃƒÂ©gios de administrador")
        print()

    try:
        # Baixar o instalador
        installer_path = download_vscode()
        if not installer_path:
            return 1

        # Executar instalaÃƒÂ§ÃƒÂ£o
        success = install_vscode(installer_path)

        # Limpar arquivo temporÃƒÂ¡rio
        cleanup(installer_path)

        if success:
            print("\nÃ°Å¸Å½â€° InstalaÃƒÂ§ÃƒÂ£o concluÃƒÂ­da com sucesso!")
            print("   O VS Code estÃƒÂ¡ pronto para uso.")
            return 0
        else:
            print("\nÃ¢ÂÅ’ Falha na instalaÃƒÂ§ÃƒÂ£o.")
            print("   Tente executar o script novamente como administrador.")
            return 1

    except KeyboardInterrupt:
        print("\n\nÃ¢Å¡Â Ã¯Â¸Â  InstalaÃƒÂ§ÃƒÂ£o cancelada pelo usuÃƒÂ¡rio.")
        return 1
    except Exception as e:
        print(f"\nÃ¢ÂÅ’ Erro inesperado: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
