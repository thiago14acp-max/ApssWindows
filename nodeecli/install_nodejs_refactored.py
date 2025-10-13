#!/usr/bin/env python3
"""
Instalador Automático do Node.js para Windows (Versão Modularizada)

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
import argparse
import time

# Importar os módulos modularizados
try:
    from modules.common import (
        Logger, configure_stdout_stderr, detectar_arquitetura, 
        verificar_permissoes_admin, detectar_nvm_windows, 
        configurar_execution_policy
    )
    from modules.nodejs_installer import NodejsInstaller
    from modules.gemini_cli_installer import GeminiCliInstaller
    from modules.qwen_cli_installer import QwenCliInstaller
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Verifique se os módulos estão no diretório 'modules' corretamente.")
    sys.exit(1)

# Verificar se a biblioteca requests está instalada
try:
    import requests
except ImportError:
    print("Erro: A biblioteca 'requests' não está instalada.")
    print("Execute o seguinte comando para instalá-la:")
    print("pip install requests")
    sys.exit(1)


def verificar_versao_windows(args):
    """
    Verifica a versão do Windows e exibe aviso se necessário.
    
    Args:
        args: Argumentos de linha de comando parseados
        
    Returns:
        int: 0 para continuar, 2 para cancelar
    """
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
    
    return 0


def verificar_permissoes_e_configurar(args):
    """
    Verifica permissões de administrador e configura o ambiente.
    
    Args:
        args: Argumentos de linha de comando parseados
        
    Returns:
        int: 0 para continuar, 2 para cancelar
    """
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
    
    return 0


def criar_sessao_http(args):
    """
    Cria e configura uma sessão HTTP com suporte a proxy.
    
    Args:
        args: Argumentos de linha de comando parseados
        
    Returns:
        requests.Session: Sessão HTTP configurada
    """
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
            sys.exit(1)
    
    return session


def exibir_resumo_instalacao(nodejs_sucesso, nodejs_versao, gemini_sucesso, qwen_sucesso):
    """
    Exibe um resumo final da instalação.
    
    Args:
        nodejs_sucesso (bool): Status da instalação do Node.js
        nodejs_versao (str): Versão do Node.js instalada
        gemini_sucesso (bool): Status da instalação do Gemini CLI
        qwen_sucesso (bool): Status da instalação do Qwen CLI
    """
    print("\n" + "=" * 60)
    print("RESUMO DA INSTALAÇÃO")
    print("=" * 60)
    
    print(f"Node.js: {'✅ SUCESSO' if nodejs_sucesso else '❌ FALHA'}")
    if nodejs_sucesso and nodejs_versao:
        print(f"  Versão: {nodejs_versao}")
    
    print(f"Gemini CLI: {'✅ SUCESSO' if gemini_sucesso else '❌ FALHA'}")
    print(f"Qwen CLI: {'✅ SUCESSO' if qwen_sucesso else '❌ FALHA'}")
    
    print("\n" + "=" * 60)


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
  python install_nodejs_refactored.py           # Modo interativo padrão
  python install_nodejs_refactored.py -y        # Prossiga sem prompts (para automação)
  python install_nodejs_refactored.py --yes     # Mesmo que -y
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
    logger = Logger(verbose=args.verbose, log_file=args.log_file)

    # Verificar se estamos executando no Windows
    if platform.system() != 'Windows':
        print('Este instalador suporta apenas Windows. Para Linux/macOS, use o gerenciador de pacotes apropriado.')
        print('Exemplos:')
        print('  - Linux: sudo apt install nodejs npm (Ubuntu/Debian)')
        print('  - macOS: brew install node (Homebrew)')
        return 1

    print("=" * 60)
    print("Instalador Automático do Node.js para Windows")
    print("=" * 60)

    # Verificar versão do Windows
    resultado = verificar_versao_windows(args)
    if resultado != 0:
        return resultado

    # Verificar permissões e configurar ambiente
    resultado = verificar_permissoes_e_configurar(args)
    if resultado != 0:
        return resultado

    # Criar sessão HTTP
    session = criar_sessao_http(args)

    # Inicializar instaladores
    nodejs_installer = NodejsInstaller(logger)
    gemini_installer = GeminiCliInstaller(logger)
    qwen_installer = QwenCliInstaller(logger)

    # Verificar se o Node.js já está instalado
    print("\nVerificando instalação existente do Node.js...")
    versao_atual = nodejs_installer.verificar_instalacao()

    if versao_atual:
        print(f"Node.js versão {versao_atual} está instalado.")
    else:
        print("Node.js não está instalado.")

    # Verificar se precisa instalar o Node.js
    instalar_nodejs = True
    if versao_atual and not args.version:
        # Obter versão mais recente para comparação
        from modules.nodejs_installer import obter_versao_mais_recente, comparar_versoes
        
        versao_info = obter_versao_mais_recente(session, args.track)
        if versao_info:
            versao_mais_recente = versao_info['version'].lstrip('v')
            if comparar_versoes(versao_atual, versao_mais_recente) >= 0:
                print(f"Seu Node.js (v{versao_atual}) já está atualizado!")
                instalar_nodejs = False

    # Instalar Node.js se necessário
    nodejs_sucesso = False
    nodejs_versao = versao_atual
    
    if instalar_nodejs:
        nodejs_sucesso, nodejs_versao = nodejs_installer.instalar(
            versao=args.version,
            track=args.track,
            session=session,
            download_timeout=args.download_timeout,
            install_timeout=args.install_timeout,
            all_users=args.all_users,
            auto_yes=args.yes,
            allow_arch_fallback=args.allow_arch_fallback
        )
    else:
        nodejs_sucesso = True  # Já estava atualizado
        print(" pulando instalação do Node.js (já está atualizado).")

    # Instalar CLIs adicionais
    print("\n" + "="*60)
    print("INSTALAÇÃO DAS FERRAMENTAS CLI ADICIONAIS")
    print("="*60)

    # Instalar Gemini CLI
    print("\nInstalando Gemini CLI...")
    gemini_sucesso = gemini_installer.instalar(args.npm_timeout)

    # Instalar Qwen CLI
    print("\nInstalando Qwen CLI...")
    qwen_sucesso = qwen_installer.instalar(args.npm_timeout)

    # Exibir resumo
    exibir_resumo_instalacao(nodejs_sucesso, nodejs_versao, gemini_sucesso, qwen_sucesso)

    # Fechar logger antes de retornar
    if logger:
        logger.close()

    # Determinar código de saída
    if nodejs_sucesso:
        return 0
    else:
        # Se o Node.js falhou, mas já havia uma instalação existente,
        # ainda consideramos parcialmente bem-sucedido
        if versao_atual:
            print("\nAVISO: Embora a instalação do Node.js tenha falhado,")
            print("foi detectada uma instalação existente no sistema.")
            print("As ferramentas CLI foram instaladas se possível.")
            return 0
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
