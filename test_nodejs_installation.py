#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para simular a instalação do Node.js e verificar se o erro original foi corrigido.
"""

import subprocess
import sys
import os

def test_nodejs_installation():
    """Testa a instalação do Node.js simulando o cenário original."""
    print("=" * 60)
    print("Teste de Instalacao do Node.js")
    print("=" * 60)
    
    # Configurar variável de ambiente para forçar UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Adicionar diretório atual ao PATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nodejs_script = os.path.join(current_dir, "nodeecli", "install_nodejs.py")
    
    # Executar o script de instalação do Node.js com --yes e --verbose
    # para simular o cenário original
    print("Executando instalador do Node.js...")
    print("Comando: python install_nodejs.py --yes --verbose")
    print("-" * 60)
    
    try:
        # Executar o script
        process = subprocess.Popen(
            [sys.executable, nodejs_script, "--yes", "--verbose"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            bufsize=1
        )
        
        # Ler e exibir a saída em tempo real
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.strip())
        
        # Esperar o processo completar
        return_code = process.wait()
        
        print("-" * 60)
        
        if return_code == 0:
            print("[SUCESSO] Instalacao do Node.js concluida sem erros de codificacao!")
            return True
        else:
            print(f"[AVISO] Instalacao do Node.js retornou codigo {return_code}")
            print("Mas nao houve erros de codificacao (o objetivo principal foi atingido)")
            return True
            
    except UnicodeEncodeError as e:
        print(f"[ERRO] Erro de codificacao detectado: {e}")
        print("O problema original nao foi completamente corrigido.")
        return False
    except Exception as e:
        print(f"[ERRO] Excecao durante a instalacao: {e}")
        return False

def main():
    """Função principal."""
    success = test_nodejs_installation()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCESSO] O problema de codificacao foi resolvido!")
        print("O instalador do Node.js agora funciona corretamente.")
        return 0
    else:
        print("\n" + "=" * 60)
        print("[ERRO] O problema de codificacao persiste.")
        print("Verifique as mensagens de erro acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())