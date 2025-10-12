#!/usr/bin/env python3
"""
Instalador Automático do Node.js para Windows

Este script verifica, baixa e instala/atualiza o Node.js automaticamente.
Execute este script como administrador para garantir que a instalação seja bem-sucedida.

Requisitos:
- Python 3.7 ou superior
- Biblioteca requests (pip install requests)
- Permissões de administrador
- Conexão com internet
"""

import subprocess
import sys
import os
import platform
import json
import tempfile
import argparse
import hashlib
from pathlib import Path
import time
import shutil
import logging
from datetime import datetime

# Verificar se a biblioteca requests está instalada
try:
    import requests
except ImportError:
    print("Erro: A biblioteca 'requests' não está instalada.")
    print("Execute o seguinte comando para instalá-la:")
    print("pip install requests")
    sys.exit(1)

# Sistema de logging simplificado
class Logger:
    def __init__(self, verbose=False, log_file=None):
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
        if self.log_handle:
            try:
                self.log_handle.write(message)
                self.log_handle.flush()
            except Exception:
                pass

    def print(self, message, verbose_only=False):
        if verbose_only and not self.verbose:
            return

        print(message)
        if self.log_handle:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._write_log(f"[{timestamp}] {message}\n")

    def close(self):
        if self.log_handle:
            self._write_log(f"=== Log encerrado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
            self.log_handle.close()

# Variável global para o logger
logger = None

def verificar_node_instalado():
    """
    Verifica se o Node.js está instalado e retorna a versão atual.

    Returns:
        str: Versão do Node.js instalada ou None se não estiver instalado
    """
    # Tenta verificar usando o PATH atual
    try:
        resultado = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True, timeout=10,
                                  encoding='utf-8', errors='replace')
        if resultado.returncode == 0:
            versao = resultado.stdout.strip()
            # Remove o prefixo 'v' da versão
            return versao[1:] if versao.startswith('v') else versao
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    # Se falhar, tenta verificar nos caminhos de instalação padrão do Windows
    if platform.system().lower() == 'windows':
        # Caminhos possíveis de instalação do Node.js
        possible_paths = [
            os.path.expandvars(r'%ProgramFiles%\nodejs\node.exe'),
            os.path.expandvars(r'%ProgramFiles(x86)%\nodejs\node.exe'),
            os.path.expandvars(r'%LocalAppData%\Programs\nodejs\node.exe'),
        ]

        for node_exe in possible_paths:
            if os.path.exists(node_exe):
                try:
                    resultado = subprocess.run([node_exe, '--version'],
                                              capture_output=True, text=True, timeout=10,
                                              encoding='utf-8', errors='replace')
                    if resultado.returncode == 0:
                        versao = resultado.stdout.strip()
                        # Remove o prefixo 'v' da versão
                        return versao[1:] if versao.startswith('v') else versao
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                    continue

    return None

import re

def obter_versao_mais_recente(session=None, track='lts'):
    """
    Obtém a versão mais recente do Node.js a partir da API oficial.

    Args:
        session: Sessão requests para suporte a proxy
        track: 'lts' para versões LTS, 'current' para versão atual

    Returns:
        dict: Informações da versão mais recente ou None em caso de erro
    """
    url = "https://nodejs.org/dist/index.json"
    try:
        print(f"Verificando a versão mais recente do Node.js (trilha: {track})...")

        # Usar sessão fornecida ou requests padrão
        requester = session if session else requests
        with requester.get(url, timeout=15) as response:
            response.raise_for_status()
            data = response.json()

        def parse_semver(v):
            # v like 'v22.10.0' -> (22,10,0)
            v = v.lstrip('v')
            major, minor, patch = (re.split(r"[.-]", v) + ["0","0","0"])[:3]
            return tuple(map(int, (major, minor, patch)))

        if track == 'lts':
            lts_entries = [x for x in data if x.get('lts')]
            if not lts_entries:
                print("Nenhuma versão LTS encontrada.")
                return None
            latest = max(lts_entries, key=lambda x: parse_semver(x['version']))
        else:  # current
            # Pega a versão mais recente regardless de LTS
            latest = max(data, key=lambda x: parse_semver(x['version']))

        return latest

    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao obter versão mais recente: {e}")

    return None

def comparar_versoes(v1, v2):
    """
    Compara duas versões semânticas.

    Args:
        v1 (str): Primeira versão
        v2 (str): Segunda versão

    Returns:
        int: -1 se v1 < v2, 0 se v1 == v2, 1 se v1 > v2
    """
    def normalizar_versao(v):
        # Remover sufixos de pré-release e build metadata
        # Exemplos: "1.0.0-alpha" -> "1.0.0", "1.0.0+build.1" -> "1.0.0"
        v = v.split('-')[0].split('+')[0]
        return [int(part) for part in v.split('.')]

    v1_parts = normalizar_versao(v1)
    v2_parts = normalizar_versao(v2)

    # Preencher com zeros para garantir mesmo comprimento
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))

    for i in range(max_len):
        if v1_parts[i] < v2_parts[i]:
            return -1
        elif v1_parts[i] > v2_parts[i]:
            return 1

    return 0

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

def verificar_disponibilidade_arquivo(url, requester, timeout=15):
    """
    Verifica se um arquivo está disponível usando HEAD, com fallback para GET.

    Args:
        url (str): URL do arquivo para verificar
        requester: Sessão requests para fazer a requisição
        timeout (int): Timeout em segundos

    Returns:
        int: Status code da requisição (200 se disponível, outro se não)
    """
    try:
        # Primeiro tentar HEAD request com context manager
        with requester.head(url, timeout=timeout) as response:
            # Se HEAD for bem-sucedido ou for 404 (não encontrado), retornar o status
            if response.status_code in (200, 404):
                return response.status_code

            # Se HEAD retornar 405 (Method Not Allowed) ou 403 (Forbidden),
            # tentar GET com stream=True para verificação leve
            if response.status_code in (405, 403):
                try:
                    with requester.get(url, stream=True, timeout=timeout) as get_response:
                        return get_response.status_code
                except requests.RequestException:
                    # Se GET também falhar, retornar o status original do HEAD
                    return response.status_code

            # Para outros status codes, retornar o status do HEAD
            return response.status_code

    except requests.RequestException:
        # Se HEAD falhar completamente, tentar GET como fallback
        try:
            with requester.get(url, stream=True, timeout=timeout) as get_response:
                return get_response.status_code
        except requests.RequestException:
            return None  # Indica falha completa na comunicação

def baixar_instalador(versao_info, arquitetura, session=None, download_timeout=300, auto_yes=False, allow_arch_fallback=False):
    """
    Baixa o instalador MSI do Node.js.

    Args:
        versao_info (dict): Informações da versão a ser baixada
        arquitetura (str): Arquitetura do sistema ('x64', 'arm64', ou 'x86')
        session: Sessão requests para suporte a proxy
        download_timeout (int): Timeout em segundos para downloads
        auto_yes (bool): Se True, não solicita confirmação do usuário
        allow_arch_fallback (bool): Se True, permite fallback automático de ARM64 para x64

    Returns:
        tuple: (caminho_msi, versao_efetiva) onde caminho_msi é o caminho para o arquivo MSI baixado
               ou None em caso de erro, e versao_efetiva é a versão efetivamente baixada
    """
    try:
        versao = versao_info['version']
        nome_arquivo = f"node-{versao}-{arquitetura}.msi"
        url = f"https://nodejs.org/dist/{versao}/{nome_arquivo}"

        if logger:
            logger.print(f"Verificando disponibilidade do instalador {nome_arquivo}...")
        else:
            print(f"Verificando disponibilidade do instalador {nome_arquivo}...")

        # Usar sessão fornecida ou requests padrão
        requester = session if session else requests

        # Verificar se o arquivo existe antes de baixar
        try:
            status_code = verificar_disponibilidade_arquivo(url, requester, timeout=download_timeout)
            if status_code == 404:
                if arquitetura == 'x86':
                    print(f"\nErro: O instalador x86 para Node.js {versao} não está disponível.")
                    print("Versões recentes do Node.js LTS não oferecem mais suporte para sistemas 32-bit.")

                    # Tentar encontrar uma versão mais antiga com suporte x86
                    print("\nTentando encontrar uma versão LTS mais recente com suporte x86...")

                    # Obter lista de versões disponíveis
                    index_url = "https://nodejs.org/dist/index.json"
                    try:
                        with requester.get(index_url, timeout=download_timeout) as index_response:
                            index_response.raise_for_status()
                            all_versions = index_response.json()

                        # Filtrar apenas versões LTS e verificar se têm suporte x86
                        def parse_semver(v):
                            v = v.lstrip('v')
                            major, minor, patch = (re.split(r"[.-]", v) + ["0","0","0"])[:3]
                            return tuple(map(int, (major, minor, patch)))

                        lts_versions = [v for v in all_versions if v.get('lts')]
                        lts_versions.sort(key=lambda x: parse_semver(x['version']), reverse=True)

                        for version_info in lts_versions:
                            test_version = version_info['version']
                            test_filename = f"node-{test_version}-x86.msi"
                            test_url = f"https://nodejs.org/dist/{test_version}/{test_filename}"

                            try:
                                test_status = verificar_disponibilidade_arquivo(test_url, requester, timeout=download_timeout)
                                if test_status == 200:
                                    print(f"Encontrada versão compatível: {test_version}")
                                    print(f"URL: {test_url}")
                                    nome_arquivo = test_filename
                                    url = test_url
                                    versao = test_version
                                    break
                            except requests.RequestException:
                                continue
                        else:
                            print("\nNão foi possível encontrar nenhuma versão LTS recente com suporte x86.")
                            print("Considere atualizar seu sistema para uma versão 64-bit.")
                            return None, None

                    except (requests.RequestException, json.JSONDecodeError):
                        print("\nNão foi possível verificar versões alternativas.")
                        print("Considere atualizar seu sistema para uma versão 64-bit.")
                        return None, None
                elif arquitetura == 'arm64':
                    print(f"\nAviso: O instalador ARM64 para Node.js {versao} não está disponível.")
                    print("Tentando fazer fallback para x64 (compatível via emulação)...")

                    # Tentar fallback para x64
                    fallback_filename = f"node-{versao}-x64.msi"
                    fallback_url = f"https://nodejs.org/dist/{versao}/{fallback_filename}"

                    try:
                        fallback_status = verificar_disponibilidade_arquivo(fallback_url, requester, timeout=download_timeout)
                        if fallback_status == 200:
                            print(f"Encontrado instalador x64 compatível: {fallback_filename}")
                            print("O Node.js x64 funcionará via emulação no seu sistema ARM64.")

                            # Solicitar confirmação antes de prosseguir com o fallback
                            if not auto_yes and not allow_arch_fallback:
                                print("\n⚠️  AVISO: O instalador x64 funcionará via emulação no sistema ARM64.")
                                print("Isso pode resultar em desempenho reduzido em comparação com o nativo ARM64.")
                                resposta = input("Deseja prosseguir com a instalação via emulação x64? (S/N): ").strip().upper()
                                if resposta != 'S':
                                    print("Instalação cancelada pelo usuário.")
                                    return None, None
                            else:
                                if allow_arch_fallback:
                                    print("\nModo automático (arch-fallback): Prosseguindo com instalação x64 via emulação.")
                                else:
                                    print("\nModo automático: Prosseguindo com instalação x64 via emulação.")

                            nome_arquivo = fallback_filename
                            url = fallback_url
                            # Manter a versão original
                        else:
                            print(f"\nErro: Nem o instalador ARM64 nem o x64 estão disponíveis para esta versão.")
                            return None, None
                    except requests.RequestException:
                        print(f"\nErro: Não foi possível verificar a disponibilidade do instalador x64 de fallback.")
                        return None, None
                else:
                    print(f"\nErro: O instalador para {arquitetura} não está disponível para esta versão.")
                    return None, None
            elif status_code != 200:
                print(f"\nErro ao verificar disponibilidade: Status {status_code}")
                return None, None
        except Exception as e:
            print(f"\nErro ao verificar disponibilidade do instalador: {e}")
            return None, None

        if logger:
            logger.print(f"Baixando {nome_arquivo}...")
        else:
            print(f"Baixando {nome_arquivo}...")

        # Log verbose com detalhes do download
        if logger and logger.verbose:
            logger.print(f"URL de download: {url}", verbose_only=True)

        # Obter checksums SHA256 para validação
        if logger:
            logger.print("Obtendo checksums para verificação de integridade...")
        else:
            print("Obtendo checksums para verificação de integridade...")
        shasums_url = f"https://nodejs.org/dist/{versao}/SHASUMS256.txt"
        try:
            with requester.get(shasums_url, timeout=download_timeout) as shasums_response:
                shasums_response.raise_for_status()
                shasums_content = shasums_response.text

            # Parse SHA256 checksums
            sha256_mapping = {}
            for line in shasums_content.splitlines():
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        sha256_hash = parts[0]
                        filename = parts[1]
                        sha256_mapping[filename] = sha256_hash

            # Verificar se o arquivo está nos checksums
            if nome_arquivo not in sha256_mapping:
                print(f"\nErro: O arquivo {nome_arquivo} não foi encontrado nos checksums oficiais.")
                print("Isso pode indicar um problema com a versão ou arquitetura selecionada.")
                return None, None

            expected_sha256 = sha256_mapping[nome_arquivo]
            print(f"Checksum esperado: {expected_sha256}")

        except requests.RequestException as e:
            print(f"\nErro: Não foi possível obter os checksums SHA256: {e}")
            print("Abortando instalação por segurança. Não é possível verificar a integridade do arquivo.")
            return None, None

        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.msi', delete=False) as temp_file:
            temp_path = temp_file.name

        # Baixar com barra de progresso e calcular hash simultaneamente
        with requester.get(url, stream=True, timeout=download_timeout) as response:
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            bytes_baixados = 0

            # Calcular SHA256 durante o download
            sha256_hasher = hashlib.sha256()

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        sha256_hasher.update(chunk)
                        bytes_baixados += len(chunk)

                        # Mostrar progresso
                        if total_size > 0:
                            progresso = int(50 * bytes_baixados / total_size)
                            bar = '[' + '=' * progresso + ' ' * (50 - progresso) + ']'
                            percent = int(100 * bytes_baixados / total_size)
                            print(f"\r{bar} {percent}%", end='', flush=True)

        print(f"\nDownload concluído: {temp_path}")

        # Verificar integridade do arquivo (sempre executado, pois expected_sha256 é garantido)
        actual_sha256 = sha256_hasher.hexdigest()
        print(f"Checksum calculado: {actual_sha256}")

        if actual_sha256.lower() != expected_sha256.lower():
            print("\nERRO: Verificação de integridade falhou!")
            print("O arquivo baixado está corrompido ou foi alterado.")
            print(f"Esperado: {expected_sha256}")
            print(f"Recebido: {actual_sha256}")

            # Remover arquivo corrompido
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None, None
        else:
            print("✓ Verificação de integridade concluída com sucesso!")

        return temp_path, versao

    except (requests.RequestException, IOError, KeyError) as e:
        print(f"\nErro ao baixar instalador: {e}")
        temp_path = locals().get('temp_path')
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        return None, None

def instalar_nodejs(caminho_msi, install_timeout=300, all_users=False):
    """
    Instala o Node.js usando o arquivo MSI.

    Args:
        caminho_msi (str): Caminho para o arquivo MSI
        install_timeout (int): Timeout em segundos para a instalação
        all_users (bool): Se True, instala para todos os usuários (ALLUSERS=1)

    Returns:
        bool: True se a instalação foi bem-sucedida, False caso contrário
    """
    try:
        print("Iniciando instalação do Node.js...")
        print("Isso pode levar alguns minutos...")
        print(f"Timeout configurado: {install_timeout} segundos")

        # Obter caminho absoluto do msiexec
        msiexec_path = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', 'msiexec.exe')

        # Verificar se o msiexec existe no caminho esperado
        if not os.path.exists(msiexec_path):
            print(f"Erro: msiexec não encontrado em {msiexec_path}")
            return False

        # Comando de instalação silenciosa
        comando = [
            msiexec_path, '/i', caminho_msi,
            '/quiet', '/norestart'
        ]

        # Adicionar ALLUSERS=1 se instalando para todos os usuários
        if all_users:
            comando.append('ALLUSERS=1')
            print("Instalando para todos os usuários do sistema...")
        else:
            print("Instalando apenas para o usuário atual...")

        resultado = subprocess.run(comando, timeout=install_timeout,
                                  encoding='utf-8', errors='replace')

        if resultado.returncode == 0:
            print("Instalação concluída com sucesso!")
            return True
        elif resultado.returncode == 3010:
            print("Instalação concluída com sucesso!")
            print("AVISO: Uma reinicialização do sistema é necessária para completar a instalação.")
            print("Por favor, reinicie o computador para garantir que o Node.js funcione corretamente.")
            return True
        else:
            print(f"Erro na instalação. Código de retorno: {resultado.returncode}")

            # Fornecer mensagens específicas para códigos de erro comuns
            if resultado.returncode == 1603:
                print("Erro 1603: Falha na instalação. Possíveis causas:")
                print("- Permissões de administrador insuficientes")
                print("- Conflito com outra instalação do Node.js")
                print("- Arquivos do sistema bloqueados")
                print("Tente executar o script como administrador.")
            elif resultado.returncode == 1618:
                print("Erro 1618: Outra instalação já está em andamento.")
                print("Aguarde a conclusão da instalação anterior e tente novamente.")
            elif resultado.returncode == 1625:
                print("Erro 1625: Políticas de sistema impedem a instalação.")
                print("Entre em contato com o administrador do sistema.")

            return False

    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        print(f"Erro durante a instalação: {e}")
        return False
    finally:
        # Limpar arquivo temporário
        if os.path.exists(caminho_msi):
            try:
                os.unlink(caminho_msi)
            except (OSError, PermissionError) as e:
                # Log permission errors without masking the original install result
                error_msg = f"Aviso: Não foi possível remover o arquivo temporário {caminho_msi}: {e}"
                print(error_msg)
                if logger:
                    logger.print(error_msg)

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
            if logger:
                logger.print(f"Tentando executar com: {powershell_exe}", verbose_only=True)

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
                print("✓ Política de execução do PowerShell configurada com sucesso!")
                if logger:
                    logger.print(f"Política de execução do PowerShell configurada para RemoteSigned - CurrentUser usando: {powershell_exe}", verbose_only=True)
                return True
            else:
                # Se o executável foi encontrado mas o comando falhou, não tentar outros candidatos
                # (o problema provavelmente é com a política de execução, não com o executável)
                print(f"⚠️  AVISO: Falha ao configurar política de execução (código: {resultado.returncode})")
                if resultado.stderr:
                    print(f"Detalhes: {resultado.stderr.strip()}")
                print("A instalação do Node.js continuará normalmente.")
                if logger:
                    logger.print(f"Falha ao configurar ExecutionPolicy com {powershell_exe}: {resultado.stderr if resultado.stderr else 'Erro desconhecido'}", verbose_only=True)
                return False

        except subprocess.TimeoutExpired:
            print("⚠️  AVISO: Timeout ao configurar política de execução do PowerShell.")
            print("A instalação do Node.js continuará normalmente.")
            return False
        except FileNotFoundError:
            # Se este executável não foi encontrado, tentar o próximo candidato
            if logger:
                logger.print(f"PowerShell não encontrado em: {powershell_exe}", verbose_only=True)
            continue
        except Exception as e:
            print(f"⚠️  AVISO: Erro ao configurar política de execução: {e}")
            print("A instalação do Node.js continuará normalmente.")
            if logger:
                logger.print(f"Erro ao configurar ExecutionPolicy com {powershell_exe}: {e}", verbose_only=True)
            return False

    # Se chegou aqui, nenhum candidato foi encontrado
    print("⚠️  AVISO: PowerShell não encontrado no sistema.")
    print("Tentado os seguintes caminhos:")
    for candidate in powershell_candidates:
        print(f"  - {candidate}")
    print("A instalação do Node.js continuará normalmente.")
    return False

def instalar_gemini_cli(npm_timeout=300):
    """
    Instala o pacote npm global @google/gemini-cli.

    Esta função atualiza o PATH com os diretórios do Node.js e npm,
    verifica a disponibilidade do npm e instala o pacote @google/gemini-cli
    globalmente usando o comando npm install -g.

    Args:
        npm_timeout (int): Timeout em segundos para a instalação do pacote npm

    Returns:
        bool: True se a instalação foi bem-sucedida, False caso contrário
    """
    print("\nInstalando pacote @google/gemini-cli...")

    try:
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
            if logger:
                logger.print(f"PATH atualizado com diretórios Node.js (priorizados): {os.pathsep.join(novos)}", verbose_only=True)

        # Verificar se npm está disponível
        npm_path = shutil.which('npm', path=novo_ambiente.get('PATH'))
        if not npm_path:
            print("⚠️  AVISO: npm não encontrado após a instalação do Node.js.")
            print("Tente reiniciar o terminal ou o computador e instale o pacote manualmente:")
            print("  npm install -g @google/gemini-cli")
            if logger:
                logger.print("npm não encontrado no PATH atualizado", verbose_only=True)
            return False

        if logger:
            logger.print(f"npm encontrado em: {npm_path}", verbose_only=True)

        # Executar comando npm install -g @google/gemini-cli
        comando = [npm_path, 'install', '-g', '@google/gemini-cli']

        if logger:
            logger.print(f"Executando comando: {' '.join(comando)}", verbose_only=True)
            logger.print(f"Timeout configurado: {npm_timeout} segundos", verbose_only=True)

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=npm_timeout,
            check=False,
            env=novo_ambiente,
            encoding='utf-8',
            errors='replace'
        )

        # Verificar o resultado
        if resultado.returncode == 0:
            print("✓ Pacote @google/gemini-cli instalado com sucesso!")
            if logger:
                logger.print("Instalação do @google/gemini-cli concluída com sucesso", verbose_only=True)
                if resultado.stdout:
                    logger.print(f"Saída npm: {resultado.stdout.strip()}", verbose_only=True)
            return True
        else:
            print(f"⚠️  AVISO: Falha ao instalar pacote @google/gemini-cli (código: {resultado.returncode})")
            if resultado.stderr:
                print(f"Detalhes do erro: {resultado.stderr.strip()}")
            print("Você pode instalar o pacote manualmente executando:")
            print("  npm install -g @google/gemini-cli")
            if logger:
                logger.print(f"Falha na instalação: {resultado.stderr if resultado.stderr else 'Erro desconhecido'}", verbose_only=True)
                if resultado.stdout:
                    logger.print(f"Saída stdout: {resultado.stdout.strip()}", verbose_only=True)
            return False

    except subprocess.TimeoutExpired:
        print(f"⚠️  AVISO: Timeout ao instalar pacote @google/gemini-cli ({npm_timeout} segundos).")
        print("A instalação pode ter sido parcial. Verifique manualmente com:")
        print("  npm list -g @google/gemini-cli")
        return False

    except Exception as e:
        print(f"⚠️  AVISO: Erro ao instalar pacote @google/gemini-cli: {e}")
        print("Tente instalar manualmente executando:")
        print("  npm install -g @google/gemini-cli")
        if logger:
            logger.print(f"Erro durante instalação do @google/gemini-cli: {e}", verbose_only=True)
        return False

def instalar_qwen_code(npm_timeout=300):
    """
    Instala o pacote npm global @qwen-code/qwen-code.

    Esta função atualiza o PATH com os diretórios do Node.js e npm,
    verifica a disponibilidade do npm e instala o pacote @qwen-code/qwen-code
    globalmente usando o comando npm install -g.

    Args:
        npm_timeout (int): Timeout em segundos para a instalação do pacote npm

    Returns:
        bool: True se a instalação foi bem-sucedida, False caso contrário
    """
    print("\nInstalando pacote @qwen-code/qwen-code...")

    try:
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
            if logger:
                logger.print(f"PATH atualizado com diretórios Node.js (priorizados): {os.pathsep.join(novos)}", verbose_only=True)

        # Verificar se npm está disponível
        npm_path = shutil.which('npm', path=novo_ambiente.get('PATH'))
        if not npm_path:
            print("⚠️  AVISO: npm não encontrado após a instalação do Node.js.")
            print("Tente reiniciar o terminal ou o computador e instale o pacote manualmente:")
            print("  npm install -g @qwen-code/qwen-code@latest")
            if logger:
                logger.print("npm não encontrado no PATH atualizado", verbose_only=True)
            return False

        if logger:
            logger.print(f"npm encontrado em: {npm_path}", verbose_only=True)

        # Executar comando npm install -g @qwen-code/qwen-code@latest
        comando = [npm_path, 'install', '-g', '@qwen-code/qwen-code@latest']

        if logger:
            logger.print(f"Executando comando: {' '.join(comando)}", verbose_only=True)
            logger.print(f"Timeout configurado: {npm_timeout} segundos", verbose_only=True)

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=npm_timeout,
            check=False,
            env=novo_ambiente,
            encoding='utf-8',
            errors='replace'
        )

        # Verificar o resultado
        if resultado.returncode == 0:
            print("✓ Pacote @qwen-code/qwen-code instalado com sucesso!")
            if logger:
                logger.print("Instalação do @qwen-code/qwen-code concluída com sucesso", verbose_only=True)
                if resultado.stdout:
                    logger.print(f"Saída npm: {resultado.stdout.strip()}", verbose_only=True)

            # Verificar instalação executando qwen --version
            qwen_path = shutil.which('qwen', path=novo_ambiente.get('PATH'))
            if qwen_path:
                try:
                    if logger:
                        logger.print(f"Verificando instalação com qwen --version (caminho: {qwen_path})", verbose_only=True)

                    resultado_qwen = subprocess.run(
                        [qwen_path, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False,
                        env=novo_ambiente,
                        encoding='utf-8',
                        errors='replace'
                    )

                    if resultado_qwen.returncode == 0:
                        versao_qwen = resultado_qwen.stdout.strip()
                        print(f"✓ Verificação bem-sucedida: {versao_qwen}")
                        if logger:
                            logger.print(f"Qwen Code CLI verificado: {versao_qwen}", verbose_only=True)
                    else:
                        if logger:
                            logger.print(f"qwen --version retornou código: {resultado_qwen.returncode}", verbose_only=True)
                            if resultado_qwen.stderr:
                                logger.print(f"Erro qwen --version: {resultado_qwen.stderr.strip()}", verbose_only=True)
                except Exception as e:
                    if logger:
                        logger.print(f"Erro ao executar qwen --version: {e}", verbose_only=True)
            else:
                if logger:
                    logger.print("Comando 'qwen' não encontrado no PATH após instalação", verbose_only=True)

            return True
        else:
            print(f"⚠️  AVISO: Falha ao instalar pacote @qwen-code/qwen-code (código: {resultado.returncode})")
            if resultado.stderr:
                print(f"Detalhes do erro: {resultado.stderr.strip()}")
            print("Você pode instalar o pacote manualmente executando:")
            print("  npm install -g @qwen-code/qwen-code@latest")
            if logger:
                logger.print(f"Falha na instalação: {resultado.stderr if resultado.stderr else 'Erro desconhecido'}", verbose_only=True)
                if resultado.stdout:
                    logger.print(f"Saída stdout: {resultado.stdout.strip()}", verbose_only=True)
            return False

    except subprocess.TimeoutExpired:
        print(f"⚠️  AVISO: Timeout ao instalar pacote @qwen-code/qwen-code ({npm_timeout} segundos).")
        print("A instalação pode ter sido parcial. Verifique manualmente com:")
        print("  npm list -g @qwen-code/qwen-code")
        return False

    except Exception as e:
        print(f"⚠️  AVISO: Erro ao instalar pacote @qwen-code/qwen-code: {e}")
        print("Tente instalar manualmente executando:")
        print("  npm install -g @qwen-code/qwen-code@latest")
        if logger:
            logger.print(f"Erro durante instalação do @qwen-code/qwen-code: {e}", verbose_only=True)
        return False

def main():
    """
    Função principal que orquestra todo o processo de verificação e instalação.

    Returns:
        int: Exit code (0 para sucesso, !=0 para falha/cancelamento)
    """
    # Parse argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description='Instalador Automático do Node.js para Windows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos:
  python install_nodejs.py           # Modo interativo padrão
  python install_nodejs.py -y        # Prossiga sem prompts (para automação)
  python install_nodejs.py --yes     # Mesmo que -y
        '''
    )
    parser.add_argument('-y', '--yes', action='store_true',
                       help='Prosseguir sem prompts interativos (ideal para CI/CD)')
    parser.add_argument('--proxy', type=str,
                       help='Configurar proxy para requisições HTTP/HTTPS (ex: http://proxy.empresa.com:8080)')
    parser.add_argument('--version', type=str,
                       help='Instalar versão específica do Node.js (ex: 18.19.0)')
    parser.add_argument('--track', choices=['lts', 'current'], default='lts',
                       help='Escolher trilha de lançamento (lts=current LTS, current=latest version)')
    parser.add_argument('--install-timeout', type=int, default=300,
                       help='Timeout em segundos para instalação do MSI (padrão: 300)')
    parser.add_argument('--all-users', action='store_true',
                       help='Instalar Node.js para todos os usuários (requer administrador)')
    parser.add_argument('--download-timeout', type=int, default=300,
                       help='Timeout em segundos para downloads (padrão: 300)')
    parser.add_argument('--verbose', action='store_true',
                       help='Aumentar verbosidade dos logs')
    parser.add_argument('--log-file', type=str,
                       help='Caminho do arquivo de log para salvar as mensagens')
    parser.add_argument('--allow-arch-fallback', action='store_true',
                       help='Permitir fallback automático de ARM64 para x64 sem confirmação')
    parser.add_argument('--npm-timeout', type=int, default=300,
                       help='Timeout em segundos para instalação de pacotes npm (padrão: 300)')
    parser.add_argument('--cacert', type=str,
                       help='Caminho para arquivo de certificado CA personalizado para validação SSL/TLS')
    parser.add_argument('--insecure', action='store_true',
                       help='Desativar verificação de certificado SSL/TLS (não recomendado)')

    args = parser.parse_args()

    # Inicializar sistema de logging
    global logger
    logger = Logger(verbose=args.verbose, log_file=args.log_file)

    # Verificar se estamos executando no Windows
    if platform.system() != 'Windows':
        print('Este instalador suporta apenas Windows. Para Linux/macOS, use o gerenciador de pacotes apropriado.')
        print('Exemplos:')
        print('  - Linux: sudo apt install nodejs npm (Ubuntu/Debian)')
        print('  - macOS: brew install node (Homebrew)')
        return 1

    # Verificar versão do Windows
    try:
        windows_version = sys.getwindowsversion()
        if windows_version.major < 10:
            print("\nAVISO: Detectado Windows com versão inferior ao recomendado.")
            print(f"Versão atual: {windows_version.major}.{windows_version.minor}")
            print("Este instalador foi projetado para Windows 10 ou superior.")
            print("A instalação do Node.js em versões mais antigas pode não ser suportada.")

            if not args.yes:
                resposta = input("\nDeseja continuar mesmo assim? (S/N): ").strip().upper()
                if resposta != 'S':
                    print("Execução cancelada pelo usuário.")
                    return 2  # Exit code para cancelamento pelo usuário
            else:
                print("\nModo automático: Continuando apesar da versão do Windows.")
    except:
        # Se não conseguir verificar a versão, continua com a execução
        print("\nAviso: Não foi possível verificar a versão do Windows.")

    print("=" * 60)
    print("Instalador Automático do Node.js para Windows")
    print("=" * 60)

    # Criar sessão HTTP com suporte a proxy
    session = requests.Session()

    # Configurar proxy se fornecido via argumento ou variáveis de ambiente
    proxy_url = args.proxy or os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
    if proxy_url:
        print(f"Usando proxy: {proxy_url}")
        session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        # Configurar headers para proxy
        session.headers.update({
            'User-Agent': 'Node.js-Installer-Python/1.0'
        })

    # Configurar verificação SSL/TLS para certificados corporativos
    if args.insecure:
        print("\n⚠️  AVISO: Verificação de certificado SSL/TLS desativada!")
        print("Esta opção não é recomendada e expõe a conexão a riscos de segurança.")
        print("A comunicação com servidores não será validada, podendo ser vulnerável a ataques man-in-the-middle.")
        session.verify = False
    elif args.cacert:
        if os.path.exists(args.cacert):
            print(f"Usando certificado CA personalizado: {args.cacert}")
            session.verify = args.cacert
        else:
            print(f"\nErro: Arquivo de certificado CA não encontrado: {args.cacert}")
            print("Verifique o caminho do arquivo e tente novamente.")
            return 1

    # Verificar permissões de administrador
    if not verificar_permissoes_admin():
        print("\nAVISO: Este script não está sendo executado como administrador.")
        print("A instalação pode falhar sem as permissões adequadas.")
        print("Considere executar este script como administrador.")

        if not args.yes:
            resposta = input("\nDeseja continuar mesmo assim? (S/N): ").strip().upper()
            if resposta != 'S':
                print("Execução cancelada pelo usuário.")
                return 2  # Exit code para cancelamento pelo usuário
        else:
            print("\nModo automático: Continuando sem privilégios de administrador.")
            print("A instalação pode falhar se as permissões forem insuficientes.")

    # Configurar política de execução do PowerShell
    configurar_execution_policy()

    # Detectar nvm-windows
    if detectar_nvm_windows():
        print("\n⚠️  AVISO: nvm-windows detectado no sistema!")
        print("O nvm-windows está gerenciando suas instalações do Node.js.")
        print("Instalar o Node.js via MSI pode entrar em conflito com o nvm-windows e")
        print("pode causar problemas na gestão de versões do Node.js.")
        print()
        print("É recomendado usar o nvm-windows para instalar/gerenciar versões do Node.js:")
        print("  nvm install latest")
        print("  nvm use latest")
        print()

        if not args.yes:
            resposta = input("Deseja continuar com a instalação via MSI mesmo assim? (S/N): ").strip().upper()
            if resposta != 'S':
                print("Instalação cancelada para evitar conflitos com o nvm-windows.")
                return 2  # Exit code para cancelamento pelo usuário
        else:
            print("Modo automático: Continuando apesar do conflito detectado.")

    # Verificar se o Node.js já está instalado
    print("\nVerificando instalação existente do Node.js...")
    versao_atual = verificar_node_instalado()

    if versao_atual:
        print(f"Node.js versão {versao_atual} está instalado.")
    else:
        print("Node.js não está instalado.")

    # Obter informações da versão
    versao_info = None
    versao_alvo = None

    if args.version:
        # Validação da versão específica
        versao_alvo = args.version
        if not versao_alvo.startswith('v'):
            versao_alvo = 'v' + versao_alvo

        # Validar se a versão existe
        try:
            print(f"Validando disponibilidade da versão {versao_alvo}...")
            requester = session if session else requests
            version_check_url = f"https://nodejs.org/dist/{versao_alvo}/SHASUMS256.txt"
            version_status = verificar_disponibilidade_arquivo(version_check_url, requester, timeout=10)

            if version_status != 200:
                print(f"Erro: Versão {versao_alvo} não encontrada ou não está disponível.")
                return 1

            # Criar versão_info no formato esperado
            versao_info = {'version': versao_alvo, 'lts': False}

            # Verificar se a versão já está instalada e é a mesma
            if versao_atual:
                versao_alvo_sem_v = versao_alvo[1:] if versao_alvo.startswith('v') else versao_alvo
                if comparar_versoes(versao_atual, versao_alvo_sem_v) == 0:
                    print(f"Node.js versão {versao_atual} já está instalado.")
                    print("Não é necessária reinstalação.")
                    return 0

        except requests.RequestException as e:
            print(f"Erro ao validar versão {versao_alvo}: {e}")
            return 1
    else:
        # Obter versão mais recente da trilha selecionada
        versao_info = obter_versao_mais_recente(session, args.track)
        if not versao_info:
            print("Não foi possível obter a versão mais recente do Node.js.")
            print("Verifique sua conexão com a internet e tente novamente.")
            return 1

    versao_mais_recente = versao_info['version'].lstrip('v')

    if args.version:
        alvo_sem_v = versao_alvo.lstrip('v') if versao_alvo else "desconhecida"
        print(f"Versão selecionada: {alvo_sem_v}")
    else:
        track_desc = "LTS" if args.track == 'lts' else "Current"
        print(f"Versão mais recente disponível: {versao_mais_recente} ({track_desc})")

    # Verificar se precisa atualizar (apenas se não for versão específica)
    if not args.version and versao_atual:
        if comparar_versoes(versao_atual, versao_mais_recente) >= 0:
            print(f"Seu Node.js (v{versao_atual}) já está atualizado!")
            return 0
        else:
            print(f"Seu Node.js (v{versao_atual}) está desatualizado.")
            print("Iniciando atualização...")
    else:
        print("Iniciando instalação...")

    # Detectar arquitetura
    arquitetura = detectar_arquitetura()
    print(f"Detectada arquitetura: {arquitetura}")

    # Baixar instalador
    caminho_msi, versao_efetiva = baixar_instalador(versao_info, arquitetura, session, args.download_timeout, args.yes, args.allow_arch_fallback)
    if not caminho_msi:
        print("Falha ao baixar o instalador. Operação cancelada.")
        return 1

    # Mostrar versão efetiva que será instalada
    versao_efetiva_sem_v = versao_efetiva.lstrip('v')
    print(f"Instalando Node.js {versao_efetiva_sem_v}...")

    # Instalar Node.js
    sucesso = instalar_nodejs(caminho_msi, args.install_timeout, args.all_users)

    if sucesso:
        print("\n" + "=" * 60)
        print("Processo concluído com sucesso!")

        # Verificar instalação
        time.sleep(3)  # Aguardar um pouco para o sistema registrar a instalação
        nova_versao = verificar_node_instalado()
        if nova_versao:
            print(f"Node.js versão {nova_versao} foi instalado com sucesso!")
            print("Você pode precisar reiniciar o terminal para usar o novo Node.js.")
        else:
            print("A instalação foi concluída, mas não foi possível verificar a versão.")
            print("Tente reiniciar o terminal ou o computador.")

        # Instalar pacote @google/gemini-cli
        print("\nInstalando pacote @google/gemini-cli...")
        gemini_instalado = instalar_gemini_cli(args.npm_timeout)
        if gemini_instalado:
            print("Pacote @google/gemini-cli instalado com sucesso!")
        else:
            print("⚠️  AVISO: Não foi possível instalar o pacote @google/gemini-cli.")
            print("Você pode instalá-lo manualmente executando: npm install -g @google/gemini-cli")

        # Instalar pacote @qwen-code/qwen-code
        print("\nInstalando pacote @qwen-code/qwen-code...")
        qwen_instalado = instalar_qwen_code(args.npm_timeout)
        if qwen_instalado:
            print("Pacote @qwen-code/qwen-code instalado com sucesso!")
        else:
            print("⚠️  AVISO: Não foi possível instalar o pacote @qwen-code/qwen-code.")
            print("Você pode instalá-lo manualmente executando: npm install -g @qwen-code/qwen-code@latest")

        print("=" * 60)

        # Fechar logger antes de retornar
        if logger:
            logger.close()
        return 0
    else:
        print("\nFalha na instalação. Verifique os erros acima.")
        print("Tente executar o script como administrador.")

        # Fechar logger antes de retornar
        if logger:
            logger.close()
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        print("Por favor, reporte este problema para melhoria do script.")
        sys.exit(1)