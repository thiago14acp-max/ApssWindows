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

def safe_print(text):
    """Imprime texto evitando erros de encoding no Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))



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
        safe_print("\n" + "="*50)
        safe_print("INSTALANDO GEMINI CLI")
        safe_print("="*50)
        safe_print("Verificando e instalando o pacote @google/gemini-cli...")


        try:
            # Verificar se Node.js está instalado
            nodejs_versao = self.verificar_nodejs()
            if not nodejs_versao:
                safe_print("❌ ERRO: Node.js não está instalado.")
                safe_print("O Gemini CLI requer o Node.js para funcionar.")
                safe_print("Por favor, instale o Node.js primeiro e tente novamente.")

                if self.logger:
                    self.logger.print("ERRO: Node.js não encontrado para instalação do Gemini CLI")
                return False

            safe_print(f"✓ Node.js versão {nodejs_versao} encontrado")

            # Preparar ambiente com caminhos do Node.js
            novo_ambiente = preparar_ambiente_nodejs()

            # Verificar se npm está disponível
            npm_path = self.verificar_npm(novo_ambiente)
            if not npm_path:
                safe_print("❌ ERRO: npm não encontrado após a instalação do Node.js.")
                safe_print("Tente reiniciar o terminal ou o computador e instale o pacote manualmente:")
                safe_print("  npm install -g @google/gemini-cli")

                if self.logger:
                    self.logger.print("ERRO: npm não encontrado no PATH atualizado")
                return False

            safe_print(f"✓ npm encontrado em: {npm_path}")
            if self.logger:
                self.logger.print(f"npm encontrado em: {npm_path}", verbose_only=True)

            # Executar comando npm install -g @google/gemini-cli
            safe_print("\nExecutando instalação do @google/gemini-cli...")
            # Força o uso do npm.cmd no Windows se encontrado, para evitar problemas com shell=False
            npm_executable = npm_path
            if os.name == 'nt' and not npm_executable.lower().endswith('.cmd') and not npm_executable.lower().endswith('.exe'):
                 # Se for apenas um script, talvez precisemos invocar via node ou cmd /c, mas npm geralmente tem um .cmd wrapper
                 pass

            comando = [npm_executable, 'install', '-g', '@google/gemini-cli']

            if self.logger:
                self.logger.print(f"Executando comando: {' '.join(comando)}", verbose_only=True)
                self.logger.print(f"Timeout configurado: {npm_timeout} segundos", verbose_only=True)

            # shell=True aqui poderia ser útil para encontrar o npm no PATH do sistema se não tivéssemos o path absoluto,
            # mas como temos o path absoluto e queremos segurança, shell=False é melhor. 
            # No entanto, no Windows, executar arquivos .cmd/.bat com shell=False requer cuidado.
            # O shutil.which geralmente retorna o arquivo executável (ex: npm.cmd).
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=npm_timeout,
                check=False,
                env=novo_ambiente,
                encoding='utf-8',
                errors='replace',
                shell=False 
            )

            # Verificar o resultado
            if resultado.returncode == 0:
                safe_print("✅ SUCESSO: Pacote @google/gemini-cli instalado com sucesso!")
                if self.logger:
                    self.logger.print("SUCESSO: Instalação do @google/gemini-cli concluída com sucesso")
                    if resultado.stdout:
                        self.logger.print(f"Saída npm: {resultado.stdout.strip()}", verbose_only=True)
                
                # Verificar se o comando gemini está disponível no PATH
                safe_print("\nVerificando disponibilidade do comando 'gemini'...")
                gemini_path = self.verificar_gemini_cli(novo_ambiente)
                
                if gemini_path:
                    safe_print(f"✅ COMANDO DISPONÍVEL: Comando 'gemini' encontrado em: {gemini_path}")
                    if self.logger:
                        self.logger.print(f"VERIFICAÇÃO: Comando 'gemini' encontrado em: {gemini_path}")
                    
                    # Tentar obter versão do Gemini CLI para confirmar funcionamento
                    try:
                        safe_print("\nVerificando funcionamento do Gemini CLI...")
                        resultado_gemini = subprocess.run(
                            [gemini_path, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            check=False,
                            env=novo_ambiente,
                            encoding='utf-8',
                            errors='replace',
                            shell=False
                        )
                        
                        if resultado_gemini.returncode == 0:
                            versao_gemini = resultado_gemini.stdout.strip()
                            safe_print(f"✅ FUNCIONAMENTO CONFIRMADO: {versao_gemini}")
                            if self.logger:
                                self.logger.print(f"VERIFICAÇÃO: Gemini CLI funcionando - {versao_gemini}")
                        else:
                            safe_print("⚠️  AVISO: Comando 'gemini' encontrado, mas não respondeu ao --version")
                            if resultado_gemini.stderr:
                                safe_print(f"Detalhes: {resultado_gemini.stderr.strip()}")

                            if self.logger:
                                self.logger.print("AVISO: Gemini CLI não respondeu ao --version")
                    except Exception as e:
                        safe_print(f"⚠️  AVISO: Não foi possível verificar o funcionamento do Gemini CLI: {e}")
                        if self.logger:
                            self.logger.print(f"AVISO: Erro ao verificar funcionamento do Gemini CLI: {e}")
                    
                    # Exibir informações de uso
                    safe_print("\n" + "-"*50)
                    safe_print("INFORMAÇÕES DE USO DO GEMINI CLI")
                    safe_print("-"*50)
                    safe_print("O Gemini CLI foi instalado com sucesso!")
                    safe_print("Para começar a usar, execute:")
                    safe_print("  gemini --help           # Exibe ajuda e comandos disponíveis")
                    safe_print("  gemini init             # Inicializa configuração")
                    safe_print("  gemini chat             # Inicia um chat")
                    safe_print("-"*50)

                    return True
                else:
                    safe_print("❌ ERRO: Comando 'gemini' não encontrado no PATH após instalação")
                    safe_print("Isso pode indicar um problema na instalação ou que o PATH não foi atualizado.")
                    safe_print("Tente reiniciar o terminal ou o computador.")

                    if self.logger:
                        self.logger.print("ERRO: Comando 'gemini' não encontrado no PATH após instalação")
                    return False
            else:
                safe_print(f"❌ ERRO: Falha ao instalar pacote @google/gemini-cli (código: {resultado.returncode})")
                if resultado.stderr:
                    safe_print(f"Detalhes do erro: {resultado.stderr.strip()}")
                safe_print("\nSoluções possíveis:")
                safe_print("1. Verifique sua conexão com a internet")
                safe_print("2. Execute o comando manualmente:")
                safe_print("   npm install -g @google/gemini-cli")
                safe_print("3. Verifique se há problemas de permissão")

                if self.logger:
                    self.logger.print(f"ERRO: Falha na instalação: {resultado.stderr if resultado.stderr else 'Erro desconhecido'}")
                    if resultado.stdout:
                        self.logger.print(f"Saída stdout: {resultado.stdout.strip()}", verbose_only=True)
                return False

        except subprocess.TimeoutExpired:
            safe_print(f"⏰ TIMEOUT: A instalação do @google/gemini-cli excedeu o tempo limite ({npm_timeout} segundos).")
            safe_print("A instalação pode ter sido parcial. Verifique manualmente com:")
            safe_print("  npm list -g @google/gemini-cli")

            if self.logger:
                self.logger.print(f"TIMEOUT: Instalação do @google/gemini-cli excedeu o tempo limite")
            return False

        except Exception as e:
            safe_print(f"❌ ERRO: Ocorreu um erro ao instalar o pacote @google/gemini-cli: {e}")
            safe_print("\nSoluções possíveis:")
            safe_print("1. Tente executar o comando manualmente:")
            safe_print("   npm install -g @google/gemini-cli")
            safe_print("2. Verifique se há problemas de permissão")
            safe_print("3. Reinicie o terminal e tente novamente")

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