#!/usr/bin/env python3
"""
Script de teste para a implementação modularizada do instalador Node.js.

Este script realiza testes básicos para verificar se os módulos estão funcionando
corretamente sem realizar instalações reais.
"""

import sys
import os

# Adicionar a raiz do projeto ao sys.path para garantir que nodeecli seja importável
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def test_imports():
    """Testa se todos os módulos podem ser importados corretamente."""
    print("Testando imports dos módulos...")
    
    try:
        from nodeecli.modules.common import (
            Logger, configure_stdout_stderr, detectar_arquitetura, 
            verificar_permissoes_admin, detectar_nvm_windows, 
            configurar_execution_policy, preparar_ambiente_nodejs
        )
        print("✓ Módulo common importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo common: {e}")
        return False
    
    try:
        from nodeecli.modules.nodejs_installer import (
            NodejsInstaller, verificar_node_instalado, obter_versao_mais_recente,
            comparar_versoes, verificar_disponibilidade_arquivo,
            baixar_instalador, instalar_nodejs
        )
        print("✓ Módulo nodejs_installer importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo nodejs_installer: {e}")
        return False
    
    try:
        from nodeecli.modules.gemini_cli_installer import GeminiCliInstaller
        print("✓ Módulo gemini_cli_installer importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo gemini_cli_installer: {e}")
        return False
    
    try:
        from nodeecli.modules.qwen_cli_installer import QwenCliInstaller
        print("✓ Módulo qwen_cli_installer importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo qwen_cli_installer: {e}")
        return False
    
    return True


def test_common_functionality():
    """Testa funcionalidades básicas do módulo common."""
    print("\nTestando funcionalidades do módulo common...")
    
    try:
        from nodeecli.modules.common import (
            detectar_arquitetura, verificar_permissoes_admin, 
            detectar_nvm_windows, preparar_ambiente_nodejs, Logger
        )
        
        # Testar detecção de arquitetura
        arch = detectar_arquitetura()
        print(f"✓ Arquitetura detectada: {arch}")
        
        # Testar verificação de permissões
        admin = verificar_permissoes_admin()
        print(f"✓ Permissões de administrador: {'Sim' if admin else 'Não'}")
        
        # Testar detecção de nvm-windows
        nvm = detectar_nvm_windows()
        print(f"✓ NVM Windows detectado: {'Sim' if nvm else 'Não'}")
        
        # Testar preparação de ambiente
        env = preparar_ambiente_nodejs()
        print(f"✓ Ambiente preparado com {len(env.get('PATH', '').split(os.pathsep))} entradas no PATH")
        
        # Testar logger
        logger = Logger(verbose=True)
        logger.print("Teste de logging do módulo common")
        logger.close()
        print("✓ Logger testado com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar funcionalidades do módulo common: {e}")
        return False


def test_installers_initialization():
    """Testa a inicialização das classes de instaladores."""
    print("\nTestando inicialização dos instaladores...")
    
    try:
        from nodeecli.modules.common import Logger
        from nodeecli.modules.nodejs_installer import NodejsInstaller
        from nodeecli.modules.gemini_cli_installer import GeminiCliInstaller
        from nodeecli.modules.qwen_cli_installer import QwenCliInstaller
        
        logger = Logger(verbose=False)
        
        # Testar inicialização do instalador Node.js
        nodejs_installer = NodejsInstaller(logger)
        print("✓ NodejsInstaller inicializado com sucesso")
        
        # Testar verificação de instalação do Node.js
        nodejs_version = nodejs_installer.verificar_instalacao()
        if nodejs_version:
            print(f"✓ Node.js versão {nodejs_version} detectado")
        else:
            print("✓ Verificação de Node.js funcionando (não detectado)")
        
        # Testar inicialização do instalador Gemini CLI
        gemini_installer = GeminiCliInstaller(logger)
        print("✓ GeminiCliInstaller inicializado com sucesso")
        
        # Testar verificação de instalação do Gemini CLI
        gemini_installed, gemini_version, gemini_path = gemini_installer.verificar_instalacao()
        if gemini_installed:
            print(f"✓ Gemini CLI detectado: {gemini_version or 'versão desconhecida'} em {gemini_path}")
        else:
            print("✓ Verificação de Gemini CLI funcionando (não detectado)")
        
        # Testar inicialização do instalador Qwen CLI
        qwen_installer = QwenCliInstaller(logger)
        print("✓ QwenCliInstaller inicializado com sucesso")
        
        # Testar verificação de instalação do Qwen CLI
        qwen_installed, qwen_version, qwen_path = qwen_installer.verificar_instalacao()
        if qwen_installed:
            print(f"✓ Qwen CLI detectado: {qwen_version or 'versão desconhecida'} em {qwen_path}")
        else:
            print("✓ Verificação de Qwen CLI funcionando (não detectado)")
        
        logger.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao testar inicialização dos instaladores: {e}")
        return False


def test_refactored_script():
    """Testa se o script refatorored pode ser importado."""
    print("\nTestando script refatorored...")
    
    try:
        # Obter o caminho para o diretório do script de teste
        test_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(test_dir, "..", "..", "nodeecli", "install_nodejs_refactored.py")

        # Verificar se o arquivo existe
        if not os.path.exists(script_path):
            print(f"❌ Arquivo {script_path} não encontrado")
            return False
        
        print("✓ Arquivo install_nodejs_refactored.py encontrado")
        
        # Tentar importar as funções principais
        import importlib.util
        spec = importlib.util.spec_from_file_location("refactored", script_path)
        refactored = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(refactored)
        
        # Verificar se as funções principais existem
        expected_functions = [
            'verificar_versao_windows',
            'verificar_permissoes_e_configurar',
            'criar_sessao_http',
            'exibir_resumo_instalacao',
            'main'
        ]
        
        for func_name in expected_functions:
            if hasattr(refactored, func_name):
                print(f"✓ Função {func_name} encontrada")
            else:
                print(f"❌ Função {func_name} não encontrada")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar script refactored: {e}")
        return False


def main():
    """Função principal de teste."""
    print("=" * 60)
    print("TESTE DA IMPLEMENTAÇÃO MODULARIZADA")
    print("=" * 60)
    
    tests = [
        ("Teste de Imports", test_imports),
        ("Teste de Funcionalidades Comuns", test_common_functionality),
        ("Teste de Inicialização de Instaladores", test_installers_initialization),
        ("Teste de Script Refatorado", test_refactored_script)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("RESULTADO DOS TESTES")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASSOU" if result else "FALHOU"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ Todos os testes passaram! A implementação modularizada está funcionando.")
        return 0
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())