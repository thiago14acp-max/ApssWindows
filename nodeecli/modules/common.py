"""
Módulo com funcionalidades comuns compartilhadas entre os instaladores.

Este módulo contém classes e funções utilitárias usadas por múltiplos
instaladores para evitar duplicação de código.
"""

import subprocess
import sys
import os
import platform
import logging
from datetime import datetime
import shutil


# Tornar a saída robusta a caracteres Unicode em consoles Windows

def configure_stdout_stderr():
    """
    Configura stdout e stderr para UTF-8 quando conectados a um terminal (TTY).
    - Evita crash ao imprimir emojis em consoles cp1252.
    - Preserva codificação original quando saída/erro são redirecionados para arquivo/pipe.
    """
    try:
        # Python 3.7+: reconfigure disponível
        if hasattr(sys.stdout, "reconfigure") and getattr(sys.stdout, "isatty", lambda: False)():
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure") and getattr(sys.stderr, "isatty", lambda: False)():
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # Em ambientes onde reconfigure não está disponível ou falha,
        # seguimos sem interromper a execução.
        pass


configure_stdout_stderr()


class Logger:
    """
    Sistema de logging simplificado para uso nos instaladores.
    """
    
    def __init__(self, verbose=False, log_file=None):
        """
        Inicializa o logger.
        
        Args:
            verbose (bool): Se True, exibe mensagens verbose
            log_file (str): Caminho para arquivo de log (opcional)
        """
        self.verbose = verbose
        self.log_file = log_file
        self.log_handle = None

        if log_file:
            try:
                self.log_handle = open(log_file, 'a', encoding='utf-8')
                self._write_log(f"=== Log iniciado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            except Exception as e:
                print(f"Erro ao abrir arquivo de log: {e}")

    def _write_log(self, message):
        """
        Escreve mensagem no arquivo de log.
        
        Args:
            message (str): Mensagem para escrever no log
        """
        if self.log_handle:
            try:
                self.log_handle.write(message)
                self.log_handle.flush()
            except Exception:
                pass

    def print(self, message, verbose_only=False):
        """
        Imprime mensagem no console e opcionalmente no arquivo de log.
        
        Args:
            message (str): Mensagem para imprimir
            verbose_only (bool): Se True, só imprime se verbose estiver ativo
        """
        if verbose_only and not self.verbose:
            return

        print(message)
        if self.log_handle:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._write_log(f"[{timestamp}] {message}\n")

    def close(self):
        """
        Fecha o arquivo de log.
        """
        if self.log_handle:
            self._write_log(f"=== Log encerrado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
            self.log_handle.close()


def detectar_arquitetura():
    """
    Detecta a arquitetura do sistema operacional.

    Returns:
        str: 'x64', 'arm64', ou 'x86' dependendo da arquitetura detectada
    """
    # Normalizar o nome da máquina
    maquina = platform.machine().lower()

    # Verificar arquiteturas baseadas no platform.machine()
    if maquina in ('amd64', 'x86_64', 'x64'):
        return 'x64'
    elif maquina in ('arm64', 'aarch64'):
        return 'arm64'

    # No Windows, verificar variáveis de ambiente para detectar corretamente
    # quando Python é 32-bit em um SO 64-bit
    if platform.system().lower() == 'windows':
        # PROCESSOR_ARCHITEW6432 indica que estamos em um processo 32-bit
        # em um sistema 64-bit (WOW64)
        proc_arch = os.environ.get('PROCESSOR_ARCHITEW6432', '').lower()
        if proc_arch in ('amd64', 'x64'):
            return 'x64'
        elif proc_arch in ('arm64',):
            return 'arm64'

        # PROCESSOR_ARCHITECTURE indica a arquitetura do processo atual
        proc_arch = os.environ.get('PROCESSOR_ARCHITECTURE', '').lower()
        if proc_arch in ('amd64', 'x64'):
            return 'x64'
        elif proc_arch in ('arm64',):
            return 'arm64'
        elif proc_arch in ('x86',):
            # Se estamos no x86, verificar se há indicação de sistema 64-bit
            # através de outras variáveis ou registro
            try:
                # Tentar verificar se existe o diretório de programas 64-bit
                program_files_x86 = os.environ.get('ProgramFiles(x86)', '')
                if program_files_x86 and os.path.exists(program_files_x86):
                    # Se existir ProgramFiles(x86), provavelmente estamos em sistema 64-bit
                    # com Python 32-bit
                    # Verificar se é ARM64 através do registro
                    try:
                        import winreg
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                          r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                                          0, winreg.KEY_READ) as key:
                            try:
                                processor_architecture, _ = winreg.QueryValueEx(key, 'PROCESSOR_ARCHITECTURE')
                                if processor_architecture.lower() == 'arm64':
                                    return 'arm64'
                                elif processor_architecture.lower() in ('amd64', 'x64'):
                                    return 'x64'
                            except OSError:
                                pass
                    except (ImportError, OSError):
                        pass
            except Exception:
                pass

    # Padrão: assumir x86 se não conseguir detectar outra arquitetura
    return 'x86'


def verificar_permissoes_admin():
    """
    Verifica se o script está sendo executado com permissões de administrador.

    Returns:
        bool: True se tem permissões de administrador, False caso contrário
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        # Se não conseguir verificar, assume que não é admin
        return False


def detectar_nvm_windows():
    """
    Detecta a presença do nvm-windows no sistema.

    Returns:
        bool: True se nvm-windows está detectado, False caso contrário
    """
    # Verificar se o comando 'nvm' está no PATH
    if shutil.which('nvm'):
        return True

    # Verificar variáveis de ambiente do nvm-windows
    if os.environ.get('NVM_HOME') or os.environ.get('NVM_SYMLINK'):
        return True

    return False


def configurar_execution_policy():
    """
    Configura a política de execução do PowerShell para RemoteSigned.

    Esta função executa o comando Set-ExecutionPolicy para permitir a execução
    de scripts PowerShell assinados remotamente, necessário para algumas
    operações do Node.js e npm.

    Returns:
        bool: True se a configuração foi bem-sucedida ou já estava configurada,
              False se houve erro (mas não interrompe o fluxo)
    """
    print("\nConfigurando política de execução do PowerShell...")

    # Tentar diferentes caminhos para o PowerShell em ordem de preferência
    powershell_candidates = []

    # 1. Caminho completo do Windows PowerShell (mais comum e disponível)
    system_root = os.environ.get('SystemRoot', r'C:\Windows')
    powershell_full_path = os.path.join(system_root, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    if os.path.exists(powershell_full_path):
        powershell_candidates.append(powershell_full_path)

    # 2. powershell.exe no PATH (padrão)
    powershell_candidates.append('powershell.exe')

    # 3. pwsh.exe (PowerShell Core/7) se disponível
    pwsh_path = shutil.which('pwsh')
    if pwsh_path:
        powershell_candidates.append(pwsh_path)
    else:
        # Tentar caminho comum para PowerShell 7
        pwsh_program_files = os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'PowerShell', '7', 'pwsh.exe')
        if os.path.exists(pwsh_program_files):
            powershell_candidates.append(pwsh_program_files)

    # Tentar executar com cada candidato até encontrar um que funcione
    for powershell_exe in powershell_candidates:
        try:
            # Construir o comando PowerShell
            comando = [
                powershell_exe, '-Command',
                'Set-ExecutionPolicy', 'RemoteSigned',
                '-Scope', 'CurrentUser', '-Force'
            ]

            # Executar o comando usando subprocess com codificação UTF-8
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                encoding='utf-8',
                errors='replace'
            )

            # Verificar o resultado
            if resultado.returncode == 0:
                print("✅ Política de execução do PowerShell configurada com sucesso!")
                return True
            else:
                # Se o executável foi encontrado mas o comando falhou, não tentar outros candidatos
                # (o problema provavelmente é com a política de execução, não com o executável)
                print(f"⚠️  AVISO: Falha ao configurar política de execução (código: {resultado.returncode})")
                if resultado.stderr:
                    print(f"Detalhes: {resultado.stderr.strip()}")
                print("A instalação do Node.js continuará normalmente.")
                return False

        except subprocess.TimeoutExpired:
            print("⚠️  AVISO: Timeout ao configurar política de execução do PowerShell.")
            print("A instalação do Node.js continuará normalmente.")
            return False
        except FileNotFoundError:
            # Se este executável não foi encontrado, tentar o próximo candidato
            continue
        except Exception as e:
            print(f"⚠️  AVISO: Erro ao configurar política de execução: {e}")
            print("A instalação do Node.js continuará normalmente.")
            return False

    # Se chegou aqui, nenhum candidato foi encontrado
    print("⚠️  AVISO: PowerShell não encontrado no sistema.")
    print("Tentado os seguintes caminhos:")
    for candidate in powershell_candidates:
        print(f"  - {candidate}")
    print("A instalação do Node.js continuará normalmente.")
    return False


def preparar_ambiente_nodejs():
    """
    Prepara o ambiente com os caminhos do Node.js para uso com subprocess.

    Returns:
        dict: Ambiente modificado com os caminhos do Node.js no PATH
    """
    # Criar cópia do ambiente atual e atualizar PATH com diretórios do Node.js
    novo_ambiente = os.environ.copy()

    # Adicionar diretórios do Node.js ao PATH
    nodejs_paths = [
        os.path.expandvars(r'%ProgramFiles%\nodejs'),
        os.path.expandvars(r'%ProgramFiles(x86)%\nodejs'),
        os.path.expandvars(r'%LocalAppData%\Programs\nodejs'),
        os.path.expandvars(r'%APPDATA%\npm'),
    ]

    # Obter PATH atual e adicionar caminhos do Node.js
    current_path = novo_ambiente.get('PATH', '')
    paths_atual = [p for p in current_path.split(os.pathsep) if p]
    novos = []

    for path in nodejs_paths:
        if os.path.exists(path) and path not in paths_atual:
            novos.append(path)

    if novos:
        updated_parts = novos + paths_atual  # prepend para priorizar
        novo_ambiente['PATH'] = os.pathsep.join(updated_parts)

    return novo_ambiente