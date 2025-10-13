"""
Módulo para instalação do Node.js no Windows.

Este módulo encapsula toda a lógica de detecção, download e instalação
do Node.js, incluindo verificação de versão, validação de integridade
e configuração do ambiente.
"""

import subprocess
import sys
import os
import platform
import json
import tempfile
import hashlib
from pathlib import Path
import time
import shutil
import re

# Verificar se a biblioteca requests está instalada
try:
    import requests
except ImportError:
    print("Erro: A biblioteca 'requests' não está instalada.")
    print("Execute o seguinte comando para instalá-la:")
    print("pip install requests")
    sys.exit(1)

from .common import Logger, detectar_arquitetura, verificar_permissoes_admin, detectar_nvm_windows


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

        print(f"Baixando {nome_arquivo}...")

        # Obter checksums SHA256 para validação
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


class NodejsInstaller:
    """
    Classe principal para instalação do Node.js.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa o instalador do Node.js.
        
        Args:
            logger: Instância de Logger para registrar logs
        """
        self.logger = logger
    
    def verificar_instalacao(self):
        """
        Verifica se o Node.js já está instalado.
        
        Returns:
            str: Versão do Node.js instalada ou None se não estiver instalado
        """
        return verificar_node_instalado()
    
    def instalar(self, versao=None, track='lts', session=None, download_timeout=300, 
                 install_timeout=300, all_users=False, auto_yes=False, 
                 allow_arch_fallback=False):
        """
        Instala o Node.js com os parâmetros especificados.
        
        Args:
            versao (str): Versão específica para instalar (opcional)
            track (str): 'lts' ou 'current'
            session: Sessão requests para suporte a proxy
            download_timeout (int): Timeout para download
            install_timeout (int): Timeout para instalação
            all_users (bool): Instalar para todos os usuários
            auto_yes (bool): Modo automático sem prompts
            allow_arch_fallback (bool): Permitir fallback de arquitetura
            
        Returns:
            tuple: (sucesso, versao_instalada)
        """
        # Verificar se o Node.js já está instalado
        versao_atual = self.verificar_instalacao()
        
        if versao_atual:
            print(f"Node.js versão {versao_atual} está instalado.")
        
        # Obter informações da versão
        versao_info = None
        versao_alvo = None
        
        if versao:
            # Validação da versão específica
            versao_alvo = versao
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
                    return False, None

                # Criar versao_info no formato esperado
                versao_info = {'version': versao_alvo, 'lts': False}

                # Verificar se a versão já está instalada e é a mesma
                if versao_atual:
                    versao_alvo_sem_v = versao_alvo[1:] if versao_alvo.startswith('v') else versao_alvo
                    if comparar_versoes(versao_atual, versao_alvo_sem_v) == 0:
                        print(f"Node.js versão {versao_atual} já está instalado.")
                        print("Não é necessária reinstalação.")
                        return True, versao_atual

            except requests.RequestException as e:
                print(f"Erro ao validar versão {versao_alvo}: {e}")
                return False, None
        else:
            # Obter versão mais recente da trilha selecionada
            versao_info = obter_versao_mais_recente(session, track)
            if not versao_info:
                print("Não foi possível obter a versão mais recente do Node.js.")
                print("Verifique sua conexão com a internet e tente novamente.")
                return False, None

        versao_mais_recente = versao_info['version'].lstrip('v')

        if versao:
            alvo_sem_v = versao_alvo.lstrip('v') if versao_alvo else "desconhecida"
            print(f"Versão selecionada: {alvo_sem_v}")
        else:
            track_desc = "LTS" if track == 'lts' else "Current"
            print(f"Versão mais recente disponível: {versao_mais_recente} ({track_desc})")

        # Verificar se precisa atualizar (apenas se não for versão específica)
        if not versao and versao_atual:
            if comparar_versoes(versao_atual, versao_mais_recente) >= 0:
                print(f"Seu Node.js (v{versao_atual}) já está atualizado!")
                return True, versao_atual
            else:
                print(f"Seu Node.js (v{versao_atual}) está desatualizado.")
                print("Iniciando atualização...")
        else:
            print("Iniciando instalação...")

        # Detectar arquitetura
        arquitetura = detectar_arquitetura()
        print(f"Detectada arquitetura: {arquitetura}")

        # Baixar instalador
        caminho_msi, versao_efetiva = baixar_instalador(versao_info, arquitetura, session, 
                                                        download_timeout, auto_yes, allow_arch_fallback)
        if not caminho_msi:
            print("Falha ao baixar o instalador. Operação cancelada.")
            return False, None

        # Mostrar versão efetiva que será instalada
        versao_efetiva_sem_v = versao_efetiva.lstrip('v')
        print(f"Instalando Node.js {versao_efetiva_sem_v}...")

        # Instalar Node.js
        sucesso = instalar_nodejs(caminho_msi, install_timeout, all_users)

        if sucesso:
            print("\nProcesso concluído com sucesso!")

            # Verificar instalação
            time.sleep(3)  # Aguardar um pouco para o sistema registrar a instalação
            nova_versao = self.verificar_instalacao()
            if nova_versao:
                print(f"Node.js versão {nova_versao} foi instalado com sucesso!")
                print("Você pode precisar reiniciar o terminal para usar o novo Node.js.")
                return True, nova_versao
            else:
                print("A instalação foi concluída, mas não foi possível verificar a versão.")
                print("Tente reiniciar o terminal ou o computador.")
                return True, versao_efetiva_sem_v
        else:
            print("\nFalha na instalação. Verifique os erros acima.")
            print("Tente executar o script como administrador.")
            return False, None