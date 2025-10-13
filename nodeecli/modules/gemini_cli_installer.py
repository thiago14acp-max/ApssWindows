"""
Módulo para instalação do Gemini CLI.

Este módulo encapsula toda a lógica de instalação do pacote @google/gemini-cli
via npm, incluindo verificação de pré-requisitos e validação pós-instalação.
"""

import subprocess
import sys
import os
import shutil

from .common import Logger, preparar_ambiente_nodejs


class GeminiCliInstaller:
    """
    Classe para instalação do Gemini CLI.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa o instalador do Gemini CLI.
        
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
    
    def verificar_gemini_cli(self, ambiente=None):
        """
        Verifica se o Gemini CLI já está instalado.
        
        Args:
            ambiente: Dicionário de ambiente para usar na verificação
            
        Returns:
            str: Caminho para o executável gemini ou None se não encontrado
        """
        return shutil.which('gemini', path=ambiente.get('PATH') if ambiente else None)
    
    def instalar(self, npm_timeout=300):
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
        print("\n" + "="*50)
        print("INSTALANDO GEMINI CLI")
        print("="*50)
        print("Verificando e instalando o pacote @google/gemini-cli...")

        try:
            # Verificar se Node.js está instalado
            nodejs_versao = self.verificar_nodejs()
            if not nodejs_versao:
                print("❌ ERRO: Node.js não está instalado.")
                print("O Gemini CLI requer o Node.js para funcionar.")
                print("Por favor, instale o Node.js primeiro e tente novamente.")
                if self.logger:
                    self.logger.print("ERRO: Node.js não encontrado para instalação do Gemini CLI")
                return False

            print(f"✓ Node.js versão {nodejs_versao} encontrado")

            # Preparar ambiente com caminhos do Node.js
            novo_ambiente = preparar_ambiente_nodejs()

            # Verificar se npm está disponível
            npm_path = self.verificar_npm(novo_ambiente)
            if not npm_path:
                print("❌ ERRO: npm não encontrado após a instalação do Node.js.")
                print("Tente reiniciar o terminal ou o computador e instale o pacote manualmente:")
                print("  npm install -g @google/gemini-cli")
                if self.logger:
                    self.logger.print("ERRO: npm não encontrado no PATH atualizado")
                return False

            print(f"✓ npm encontrado em: {npm_path}")
            if self.logger:
                self.logger.print(f"npm encontrado em: {npm_path}", verbose_only=True)

            # Executar comando npm install -g @google/gemini-cli
            print("\nExecutando instalação do @google/gemini-cli...")
            comando = [npm_path, 'install', '-g', '@google/gemini-cli']

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
                print("✅ SUCESSO: Pacote @google/gemini-cli instalado com sucesso!")
                if self.logger:
                    self.logger.print("SUCESSO: Instalação do @google/gemini-cli concluída com sucesso")
                    if resultado.stdout:
                        self.logger.print(f"Saída npm: {resultado.stdout.strip()}", verbose_only=True)
                
                # Verificar se o comando gemini está disponível no PATH
                print("\nVerificando disponibilidade do comando 'gemini'...")
                gemini_path = self.verificar_gemini_cli(novo_ambiente)
                
                if gemini_path:
                    print(f"✅ COMANDO DISPONÍVEL: Comando 'gemini' encontrado em: {gemini_path}")
                    if self.logger:
                        self.logger.print(f"VERIFICAÇÃO: Comando 'gemini' encontrado em: {gemini_path}")
                    
                    # Tentar obter versão do Gemini CLI para confirmar funcionamento
                    try:
                        print("\nVerificando funcionamento do Gemini CLI...")
                        resultado_gemini = subprocess.run(
                            [gemini_path, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            check=False,
                            env=novo_ambiente,
                            encoding='utf-8',
                            errors='replace'
                        )
                        
                        if resultado_gemini.returncode == 0:
                            versao_gemini = resultado_gemini.stdout.strip()
                            print(f"✅ FUNCIONAMENTO CONFIRMADO: {versao_gemini}")
                            if self.logger:
                                self.logger.print(f"VERIFICAÇÃO: Gemini CLI funcionando - {versao_gemini}")
                        else:
                            print("⚠️  AVISO: Comando 'gemini' encontrado, mas não respondeu ao --version")
                            if resultado_gemini.stderr:
                                print(f"Detalhes: {resultado_gemini.stderr.strip()}")
                            if self.logger:
                                self.logger.print("AVISO: Gemini CLI não respondeu ao --version")
                    except Exception as e:
                        print(f"⚠️  AVISO: Não foi possível verificar o funcionamento do Gemini CLI: {e}")
                        if self.logger:
                            self.logger.print(f"AVISO: Erro ao verificar funcionamento do Gemini CLI: {e}")
                    
                    # Exibir informações de uso
                    print("\n" + "-"*50)
                    print("INFORMAÇÕES DE USO DO GEMINI CLI")
                    print("-"*50)
                    print("O Gemini CLI foi instalado com sucesso!")
                    print("Para começar a usar, execute:")
                    print("  gemini --help           # Exibe ajuda e comandos disponíveis")
                    print("  gemini init             # Inicializa configuração")
                    print("  gemini chat             # Inicia um chat")
                    print("-"*50)
                    
                    return True
                else:
                    print("❌ ERRO: Comando 'gemini' não encontrado no PATH após instalação")
                    print("Isso pode indicar um problema na instalação ou que o PATH não foi atualizado.")
                    print("Tente reiniciar o terminal ou o computador.")
                    if self.logger:
                        self.logger.print("ERRO: Comando 'gemini' não encontrado no PATH após instalação")
                    return False
            else:
                print(f"❌ ERRO: Falha ao instalar pacote @google/gemini-cli (código: {resultado.returncode})")
                if resultado.stderr:
                    print(f"Detalhes do erro: {resultado.stderr.strip()}")
                print("\nSoluções possíveis:")
                print("1. Verifique sua conexão com a internet")
                print("2. Execute o comando manualmente:")
                print("   npm install -g @google/gemini-cli")
                print("3. Verifique se há problemas de permissão")
                if self.logger:
                    self.logger.print(f"ERRO: Falha na instalação: {resultado.stderr if resultado.stderr else 'Erro desconhecido'}")
                    if resultado.stdout:
                        self.logger.print(f"Saída stdout: {resultado.stdout.strip()}", verbose_only=True)
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT: A instalação do @google/gemini-cli excedeu o tempo limite ({npm_timeout} segundos).")
            print("A instalação pode ter sido parcial. Verifique manualmente com:")
            print("  npm list -g @google/gemini-cli")
            if self.logger:
                self.logger.print(f"TIMEOUT: Instalação do @google/gemini-cli excedeu o tempo limite")
            return False

        except Exception as e:
            print(f"❌ ERRO: Ocorreu um erro ao instalar o pacote @google/gemini-cli: {e}")
            print("\nSoluções possíveis:")
            print("1. Tente executar o comando manualmente:")
            print("   npm install -g @google/gemini-cli")
            print("2. Verifique se há problemas de permissão")
            print("3. Reinicie o terminal e tente novamente")
            if self.logger:
                self.logger.print(f"ERRO: Exceção durante instalação do @google/gemini-cli: {e}")
            return False
    
    def verificar_instalacao(self):
        """
        Verifica se o Gemini CLI está instalado e funcionando.
        
        Returns:
            tuple: (instalado, versao, comando_path)
        """
        ambiente = preparar_ambiente_nodejs()
        gemini_path = self.verificar_gemini_cli(ambiente)
        
        if not gemini_path:
            return False, None, None
        
        try:
            resultado = subprocess.run(
                [gemini_path, '--version'],
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
                return True, versao, gemini_path
        except Exception:
            pass
        
        return True, None, gemini_path