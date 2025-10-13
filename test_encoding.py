#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar se os problemas de codificação foram resolvidos.
"""

import subprocess
import sys
import os

def test_nodejs_script():
    """Testa a execução do script de instalação do Node.js com caracteres especiais."""
    print("Testando script de instalacao do Node.js...")
    
    # Adicionar diretório atual ao PATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nodejs_script = os.path.join(current_dir, "nodeecli", "install_nodejs_refactored.py")
    
    # Configurar variável de ambiente para forçar UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Executar script com --help para testar apenas a inicialização
    try:
        result = subprocess.run(
            [sys.executable, nodejs_script, "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=10
        )
        
        if result.returncode == 0:
            print("[OK] Script do Node.js executou sem erros de codificacao")
            return True
        else:
            print(f"[ERRO] Erro ao executar script do Node.js: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Excecao ao executar script do Node.js: {e}")
        return False

def test_vscode_script():
    """Testa a sintaxe do script de instalação do VS Code com caracteres especiais."""
    print("Testando script de instalacao do VS Code...")
    
    # Adicionar diretório atual ao PATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vscode_script = os.path.join(current_dir, "vscode", "vscode_installer.py")
    
    # Configurar variável de ambiente para forçar UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Testar compilação do script para verificar se há erros de sintaxe/codificação
    try:
        # Compilar o script para verificar se há erros de sintaxe
        with open(vscode_script, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Tentar compilar o código
        compile(source_code, vscode_script, 'exec')
        
        print("[OK] Script do VS Code compilado sem erros de codificacao")
        return True
            
    except Exception as e:
        print(f"[ERRO] Excecao ao compilar script do VS Code: {e}")
        return False

def main():
    """Função principal de teste."""
    print("=" * 60)
    print("Teste de Correcoes de Codificacao")
    print("=" * 60)
    
    # Testar scripts individuais
    nodejs_ok = test_nodejs_script()
    vscode_ok = test_vscode_script()
    
    print("\n" + "=" * 60)
    print("Resumo dos Testes:")
    print(f"Script do Node.js: {'[OK]' if nodejs_ok else '[FALHOU]'}")
    print(f"Script do VS Code: {'[OK]' if vscode_ok else '[FALHOU]'}")
    
    if nodejs_ok and vscode_ok:
        print("\n[OK] Todos os testes passaram! As correcoes de codificacao foram bem-sucedidas.")
        return 0
    else:
        print("\n[ERRO] Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
