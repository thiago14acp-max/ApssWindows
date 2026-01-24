#!/usr/bin/env python3
"""
OpenCode Installer
Automatiza o download e instalação do OpenCode CLI.
"""

import os
import sys
import subprocess
import tempfile
import requests
import time
import ctypes
import hashlib
import shutil
import logging
from pathlib import Path
from typing import Optional, List, Tuple

# Configuração de Logging simples se não houver um módulo de logger compartilhado disponível aqui
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("OpenCodeInstaller")

# --- CONFIGURAÇÃO PADRÃO ---
# Permite override via variáveis de ambiente para testes ou novos releases
DEFAULT_DOWNLOAD_URL = os.environ.get("OPENCODE_DOWNLOAD_URL", "https://example.com/download/opencode-installer-win64.exe")
# Checksum SHA256 esperado (placeholder - deve ser atualizado junto com a URL)
DEFAULT_SHA256 = os.environ.get("OPENCODE_SHA256", "0000000000000000000000000000000000000000000000000000000000000000")
MIN_DISK_SPACE_MB = 500  # Espaço mínimo necessário em MB


class OpenCodeInstaller:
    """
    Gerencia a instalação do OpenCode CLI.
    """

    def __init__(self, download_url: str = DEFAULT_DOWNLOAD_URL, expected_sha256: Optional[str] = None):
        self.download_url = download_url
        self.expected_sha256 = expected_sha256
        self.install_args = ["/S"]  # Instalação silenciosa
        self.timeout = (10, 60)

    def is_admin(self) -> bool:
        """Verifica se o script está sendo executado com privilégios de administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def verify_windows(self) -> bool:
        """Verifica se está rodando no Windows."""
        return sys.platform == "win32"

    def check_disk_space(self, required_mb: int = MIN_DISK_SPACE_MB) -> bool:
        """Verifica se há espaço suficiente em disco."""
        try:
            # Verifica no drive onde o script está rodando ou C:
            path = Path.cwd().anchor
            total, used, free = shutil.disk_usage(path)
            free_mb = free / (1024 * 1024)
            if free_mb < required_mb:
                logger.error(f"❌ Espaço em disco insuficiente. Necessário: {required_mb}MB, Disponível: {free_mb:.1f}MB")
                return False
            return True
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível verificar espaço em disco: {e}")
            return True  # Assume que tem espaço se falhar a verificação

    def verify_checksum(self, file_path: str, expected_sha256: str) -> bool:
        """Verifica o hash SHA256 do arquivo."""
        if not expected_sha256 or expected_sha256 == DEFAULT_SHA256:
            logger.warning("⚠️  Aviso: Verificação de checksum ignorada (hash não configurado).")
            return True

        logger.info("   Verificando integridade (SHA256)...")
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            file_hash = sha256_hash.hexdigest()
            if file_hash.lower() == expected_sha256.lower():
                logger.info("✅ Integridade confirmada.")
                return True
            else:
                logger.error(f"❌ Falha na verificação de integridade.")
                logger.error(f"   Esperado: {expected_sha256}")
                logger.error(f"   Obtido:   {file_hash}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao calcular checksum: {e}")
            return False

    def download(self) -> Optional[str]:
        """
        Baixa o instalador.
        Retorna o caminho do arquivo temporário ou None em caso de falha.
        """
        if not self.check_disk_space():
            return None

        logger.info("📥 Iniciando download do OpenCode...")
        logger.info(f"   URL: {self.download_url}")

        # Simulação para URL de exemplo
        if "example.com" in self.download_url:
            logger.warning("\n⚠️  AVISO: URL de placeholder detectada.")
            logger.warning("   Simulando download com sucesso para fins de validação.")
            # Cria um arquivo dummy para simular o instalador
            try:
                fd, installer_path = tempfile.mkstemp(suffix='.exe')
                os.close(fd)
                with open(installer_path, 'wb') as f:
                    f.write(b"MOCK INSTALLER CONTENT")
                return installer_path
            except Exception as e:
                logger.error(f"❌ Erro ao criar arquivo simulado: {e}")
                return None

        try:
            # Cria arquivo temporário
            fd, installer_path = tempfile.mkstemp(suffix='.exe')
            os.close(fd)  # Fecha o descritor de arquivo de baixo nível

            logger.info("   Conectando...")
            with requests.get(self.download_url, stream=True, timeout=self.timeout) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('Content-Length', 0))
                
                with open(installer_path, 'wb') as file:
                    downloaded = 0
                    chunk_size = 8192
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)

            logger.info("✅ Download concluído.")
            
            # Verificar checksum se configurado
            if self.expected_sha256:
                if not self.verify_checksum(installer_path, self.expected_sha256):
                    os.remove(installer_path)
                    return None

            return installer_path

        except requests.exceptions.RequestException as e:
            logger.error(f"\n❌ Erro no download: {e}")
            return None
        except Exception as e:
            logger.error(f"\n❌ Erro inesperado durante download: {e}")
            if 'installer_path' in locals() and os.path.exists(installer_path):
                os.remove(installer_path)
            return None

    def install_executable(self, installer_path: str) -> bool:
        """Executa o instalador baixado."""
        logger.info("\n🛠️  Instalando OpenCode...")
        
        if not os.path.exists(installer_path):
            logger.error("❌ Arquivo instalador não encontrado.")
            return False

        # Verifica se é o arquivo dummy
        try:
            with open(installer_path, 'rb') as f:
                content = f.read()
                if content == b"MOCK INSTALLER CONTENT":
                    logger.info("ℹ️  Modo Simulação: Execução do instalador real ignorada.")
                    logger.info("✅ Instalação simulada com sucesso!")
                    return True
        except Exception:
            pass

        # Garante que args e caminho estejam seguros
        cmd = [str(installer_path)] + self.install_args
        logger.info(f"   Executando: {' '.join(cmd)}")

        try:
            # shell=False é o padrão, mas explicitando por segurança
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            
            if result.returncode == 0:
                logger.info("✅ Instalação executada com sucesso!")
                return True
            else:
                logger.error(f"❌ Falha na instalação (Código {result.returncode})")
                if result.stderr:
                    logger.error(f"   Erro: {result.stderr.strip()}")
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao executar instalador: {e}")
            return False

    def install(self) -> bool:
        """Fluxo completo de instalação."""
        print_banner()

        if not self.verify_windows():
            logger.error("❌ Erro: Este script só funciona no Windows.")
            return False

        if not self.is_admin():
            logger.warning("ℹ️  Nota: Executando sem privilégios de administrador.")
            logger.warning("   Recomendado executar como Administrador para instalação correta.\n")

        installer_path = self.download()
        
        # Se falhou no download (e não retornou path nem simulado)
        if not installer_path:
            return False

        try:
            success = self.install_executable(installer_path)
        finally:
            # Limpeza
            if os.path.exists(installer_path):
                try:
                    os.remove(installer_path)
                except Exception:
                    pass
        
        return success


def print_banner():
    """Exibe banner de boas-vindas."""
    print("=" * 60)
    print("    OpenCode CLI Installer")
    print("    Instalação automatizada do OpenCode CLI no Windows")
    print("=" * 60)
    print()


def main():
    installer = OpenCodeInstaller()
    if installer.install():
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

