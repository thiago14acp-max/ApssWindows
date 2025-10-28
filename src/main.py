
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador de Instalações - Ponto de Entrada da Aplicação
"""
import sys
import os
import ctypes

# Adicionar o diretório raiz do projeto ao sys.path
# Isso garante que as importações de 'src' funcionem corretamente
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ui.main_view import MainView
from src.app.orchestrator import OrchestratorApp

def main() -> None:
    """Ponto de entrada da aplicação."""
    # Configuração de High-DPI para Windows
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass  # Não é Windows ou ocorreu um erro

    root = MainView()
    app = OrchestratorApp(root)
    app.run()

if __name__ == "__main__":
    main()
