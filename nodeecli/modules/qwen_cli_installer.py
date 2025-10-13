"""
Módulo para instalação do Qwen CLI.

Este módulo encapsula toda a lógica de instalação do pacote @qwen-code/qwen-code
via npm, incluindo verificação de pré-requisitos e validação pós-instalação.
"""

import subprocess
import sys
import os
import shutil

from .common import Logger, preparar_ambiente_nodejs


class QwenCliInstaller:
    """
    Classe para instalação do Qwen CLI.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa o instalador do Qwen CLI.
        
        Args:
            logger: Instância de Logger para registrar logs
        """
        self.logger = logger
    
    def verificar_nodejs(self):
        """
        Verifica se o Node.js está instalado.
        
        Returns:
            str: Versão do Node.js instalada ou None se não estiver instalado
        """
        try:
            resultado = subprocess.run(['node', '--version'],
                                      capture_output=True, text=True, timeout=10,
                                      encoding='utf-8', errors='replace')
            if resultado.returncode == 0:
                versao = resultado.stdout.strip()
                return versao[1:] if versao.startswith('v') else versao
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        return None
    
    def verificar_npm(self, ambiente=None):
        """
        Verifica se o npm está disponível no ambiente.
        
        Args:
            ambiente: Dicionário de ambiente para usar na verificação
            
        Returns:
            str: Caminho para o executável npm ou None se não encontrado
        """
        return shutil.which('npm', path=ambiente.get('PATH') if ambiente else None)
    
    def verificar_qwen_cli(self, ambiente=None):
        """
        Verifica se o Qwen CLI já está instalado.
        
        Args:
            ambiente: Dicionário de ambiente para usar na verificação
            
        Returns:
            str: Caminho para o executável qwen ou None se não encontrado
        """
        return shutil.which('qwen', path=ambiente.get('PATH') if ambiente else None)
    
    def instalar(self, npm_timeout=300):
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
        print("\n" + "="*50)
        print("INSTALANDO QWEN CLI")
        print("="*50)
        print("Verificando e instalando o pacote @qwen-code/qwen-code...")

        try:
            # Verificar se Node.js está instalado
            nodejs_versao = self.verificar_nodejs()
            if not nodejs_versao:
                print("❌ ERRO: Node.js não está instalado.")
                print("O Qwen CLI requer o Node.js para funcionar.")
                print("Por favor, instale o Node.js primeiro e tente novamente.")
                if self.logger:
                    self.logger.print("ERRO: Node.js não encontrado para instalação do Qwen CLI")
                return False

            print(f"✓ Node.js versão {nodejs_versao} encontrado")

            # Preparar ambiente com caminhos do Node.js
            novo_ambiente = preparar_ambiente_nodejs()

            # Verificar se npm está disponível
            npm_path = self.verificar_npm(novo_ambiente)
            if not npm_path:
                print("⚠️  AVISO: npm não encontrado após a instalação do Node.js.")
                print("Tente reiniciar o terminal ou o computador e instale o pacote manualmente:")
                print("  npm install -g @qwen-code/qwen-code@latest")
                if self.logger:
                    self.logger.print("npm não encontrado no PATH atualizado", verbose_only=True)
                return False

            if self.logger:
                self.logger.print(f"npm encontrado em: {npm_path}", verbose_only=True)

            # Executar comando npm install -g @qwen-code/qwen-code@latest
            print("\nExecutando instalação do @qwen-code/qwen-code...")
            comando = [npm_path, 'install', '-g', '@qwen-code/qwen-code@latest']

            if self.logger:
                self.logger.print(f"Executando comando: {' '.join(comando)}", verbose_only=True)
                self.logger.print(f"Timeout configurado: {npm_timeout} segundos", verbose_only=True)

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
                if self.logger:
                    self.logger.print("Instalação do @qwen-code/qwen-code concluída com sucesso", verbose_only=True)
                    if resultado.stdout:
                        self.logger.print(f"Saída npm: {resultado.stdout.strip()}", verbose_only=True)

                # Verificar instalação executando qwen --version
                qwen_path = self.verificar_qwen_cli(novo_ambiente)
                if qwen_path:
                    try:
                        if self.logger:
                            self.logger.print(f"Verificando instalação com qwen --version (caminho: {qwen_path})", verbose_only=True)

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
                            if self.logger:
                                self.logger.print(f"Qwen Code CLI verificado: {versao_qwen}", verbose_only=True)
                        else:
                            if self.logger:
                                self.logger.print(f"qwen --version retornou código: {resultado_qwen.returncode}", verbose_only=True)
                                if resultado_qwen.stderr:
                                    self.logger.print(f"Erro qwen --version: {resultado_qwen.stderr.strip()}", verbose_only=True)
                    except Exception as e:
                        if self.logger:
                            self.logger.print(f"Erro ao executar qwen --version: {e}", verbose_only=True)
                else:
                    if self.logger:
                        self.logger.print("Comando 'qwen' não encontrado no PATH após instalação", verbose_only=True)

                # Exibir informações de uso
                print("\n" + "-"*50)
                print("INFORMAÇÕES DE USO DO QWEN CLI")
                print("-"*50)
                print("O Qwen CLI foi instalado com sucesso!")
                print("Para começar a usar, execute:")
                print("  qwen --help            # Exibe ajuda e comandos disponíveis")
                print("  qwen --version         # Verifica a versão instalada")
                print("-"*50)
                
                return True
            else:
                print(f"⚠️  AVISO: Falha ao instalar pacote @qwen-code/qwen-code (código: {resultado.returncode})")
                if resultado.stderr:
                    print(f"Detalhes do erro: {resultado.stderr.strip()}")
                print("Você pode instalar o pacote manualmente executando:")
                print("  npm install -g @qwen-code/qwen-code@latest")
                if self.logger:
                    self.logger.print(f"Falha na instalação: {resultado.stderr if resultado.stderr else 'Erro desconhecido'}", verbose_only=True)
                    if resultado.stdout:
                        self.logger.print(f"Saída stdout: {resultado.stdout.strip()}", verbose_only=True)
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
            if self.logger:
                self.logger.print(f"Erro durante instalação do @qwen-code/qwen-code: {e}", verbose_only=True)
            return False
    
    def verificar_instalacao(self):
        """
        Verifica se o Qwen CLI está instalado e funcionando.
        
        Returns:
            tuple: (instalado, versao, comando_path)
        """
        ambiente = preparar_ambiente_nodejs()
        qwen_path = self.verificar_qwen_cli(ambiente)
        
        if not qwen_path:
            return False, None, None
        
        try:
            resultado = subprocess.run(
                [qwen_path, '--version'],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                env=ambiente,
                encoding='utf-8',
                errors='replace'
            )
            
            if resultado.returncode == 0:
                versao = resultado.stdout.strip()
                return True, versao, qwen_path
        except Exception:
            pass
        
        return True, None, qwen_path