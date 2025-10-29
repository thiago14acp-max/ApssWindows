#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper de entrada para a GUI.
Permite executar a aplicação com `python srcmain.py` e é usado pelo PyInstaller.
"""
import sys

try:
    from src.main import main as _main
except Exception as e:
    # Fallback para executar o módulo diretamente se import falhar
    import runpy
    if __name__ == "__main__":
        sys.exit(runpy.run_module("src.main", run_name="__main__"))
else:
    if __name__ == "__main__":
        sys.exit(_main())

