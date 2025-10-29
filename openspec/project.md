# Contexto do Projeto

## Propósito
Ferramenta para Windows que automatiza a instalação e configuração inicial de ferramentas de desenvolvimento (Node.js, Visual Studio Code, Git e MCP Excel Server). Fornece uma interface gráfica moderna (CustomTkinter) com logs em tempo real, barra de progresso, temas e cancelamento. Empacotamento via PyInstaller para distribuição.

## Stack Tecnológica
- Linguagem: Python 3.8+
- GUI: `customtkinter` (Tkinter) e `Pillow`
- HTTP/Download: `requests`
- Empacotamento: `PyInstaller` (`orchestrator.spec`, `build_exe.bat`)
- SO alvo: Windows 10/11 (64-bit)
- Execução: `subprocess`, `ctypes`, `pathlib`, `tempfile`
- Scripts em lote: `build_exe.bat`, `install_and_run.bat`

Dependências (pip):
- `customtkinter>=5.2.0`, `Pillow>=10.0.0`, `requests>=2.31.0`, `pyinstaller>=6.0.0`

## Artefatos gerados (PyInstaller)
- `dist/OrquestradorInstalacoes.exe` (GUI principal)
- `dist/install_nodejs.exe` (instalador Node.js — console)
- `dist/vscode_installer.exe` (instalador VS Code — console)
- `dist/git_installer.exe` (instalador Git — console)
- `dist/mcp_excel_installer.exe` (instalador MCP Excel Server — console)

## Convenções do Projeto

### Estilo de Código
- Padrões próximos ao PEP 8; nomes descritivos (snake_case para funções/módulos)
- Docstrings e mensagens em Português (pt-BR); logs podem incluir emojis/ícones
- Codificação UTF-8; subprocessos com `PYTHONIOENCODING=utf-8` quando relevante

### Padrões de Arquitetura
- GUI desacoplada orquestra instaladores externos via `subprocess` em thread dedicada; comunica com a UI por `queue` (worker + message queue) para manter responsividade
- Node.js via MSI silencioso (`msiexec /quiet /norestart`) com detecção de arquitetura, validação SHA256 e detecção de `nvm-windows`
- VS Code via User Installer 64-bit com flags do Inno Setup (ícone desktop, context menu, associações e PATH)
- MCP Excel Server por clone de repositório Git para `C:/Projetos/mcp-excel-server`, criação de `.venv` com `uv venv` e instalação de dependências com `uv pip install -e .`
- Empacotamento PyInstaller: spec dedicado para GUI e cada instalador; `icon.ico` e UPX habilitado

Execução empacotada vs script:
- A GUI detecta modo empacotado (`getattr(sys, 'frozen', False)`) e invoca `install_nodejs.exe`, `vscode_installer.exe`, `git_installer.exe` e `mcp_excel_installer.exe`. Em modo script, invoca `python <script>.py`.
- Em Windows, subprocessos usam `CREATE_NO_WINDOW` para não abrir consoles adicionais.

## Como rodar localmente (dev)
- `pip install -r requirements.txt`
- `python srcmain.py`
- Para build: `build_exe.bat` (gera `dist/` via `pyinstaller orchestrator.spec --clean`)

## Estrutura do Repositório
```
Instalacoes/
├── orchestrator.spec           # Configuração PyInstaller (GUI + instaladores)
├── build_exe.bat               # Script de build
├── requirements.txt            # Dependências
├── src/
│   ├── app/                    # Orquestração e estado da aplicação
│   ├── core/                   # Serviços (ex.: InstallationService)
│   ├── ui/                     # Componentes da interface
│   └── main.py                 # Ponto de entrada da GUI
├── nodeecli/
│   ├── install_nodejs_refactored.py   # Instalador Node.js
│   └── README.md
├── vscode/
│   ├── vscode_installer.py     # Instalador VS Code
│   └── README.md
├── git/
│   └── git_installer.py        # Instalador Git for Windows
├── mcp_excel/
│   ├── mcp_excel_installer.py  # Instalador MCP Excel Server
│   └── README.md
└── openspec/
    ├── project.md              # Este documento (convenções do projeto)
    └── AGENTS.md               # Guia do OpenSpec
```

## Convenções de Logs e UX
- Logs em UTF-8; níveis/cores na GUI: `INFO` (branco), `WARNING` (amarelo), `ERROR` (vermelho), `SUCCESS` (verde)
- Mensagens curtas e acionáveis; evitar quebras multilinha desnecessárias
- Progresso: barra indeterminada no início; muda para determinada conforme etapas concluídas
- Cancelamento: botão “Cancelar” define `cancel_requested=True` e encerra subprocesso (`terminate` → `kill` de fallback), com mensagens claras
