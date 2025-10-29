# Orquestrador de Instalações

Aplicação desktop para Windows que automatiza a instalação de ferramentas de desenvolvimento como Node.js, Visual Studio Code, Git e MCP Excel Server. Interface moderna com logs em tempo real, progresso e cancelamento.

## Funcionalidades

- Interface gráfica amigável (CustomTkinter)
- Instalação automatizada de Node.js, VS Code, Git e MCP Excel Server
- Verificação de dependências e mensagens claras
- Logs em tempo real e temas (claro/escuro/sistema)

## Como Usar

### Pré-requisitos

- Windows 10 ou superior
- Python 3.7 ou superior

### Como rodar localmente

1) Clone o repositório:
```
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

2) Instale dependências e execute a GUI:
- Via script: execute `install_and_run.bat` (instala e inicia a aplicação)
- Via terminal:
```
pip install -r requirements.txt
python srcmain.py
```

## Executáveis gerados (PyInstaller)

- `dist/OrquestradorInstalacoes.exe` (GUI)
- `dist/install_nodejs.exe` (Node.js)
- `dist/vscode_installer.exe` (VS Code)
- `dist/git_installer.exe` (Git)
- `dist/mcp_excel_installer.exe` (MCP Excel Server)

## Estrutura do Projeto

- `src/`: código-fonte da aplicação
  - `app/`: orquestração e estado
  - `core/`: serviços (ex.: `InstallationService`)
  - `ui/`: componentes de interface
  - `main.py`: ponto de entrada
- `nodeecli/`: instalador do Node.js e CLIs
- `vscode/`: instalador do Visual Studio Code
- `git/`: instalador do Git for Windows
- `mcp_excel/`: instalador do MCP Excel Server
- `orchestrator.spec`: configuração do PyInstaller
- `build_exe.bat`: script de build (gera executáveis em `dist/`)
- `install_and_run.bat`: instalação e execução rápidas (Windows)
- `requirements.txt`: dependências Python
