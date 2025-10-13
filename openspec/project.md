# Contexto do Projeto

## Propósito
Ferramenta para Windows que automatiza a instalação e configuração inicial de ferramentas de desenvolvimento, com foco em Node.js e Visual Studio Code. Fornece uma interface gráfica moderna (CustomTkinter) com logs em tempo real, barra de progresso, temas, e capacidade de cancelamento, além de empacotamento em executáveis para uso por usuários finais.

Objetivos principais:
- Reduzir o atrito na preparação de ambientes Windows (10/11) para desenvolvimento.
- Padronizar instalações com opções silenciosas e seguras.
- Oferecer experiência guiada via GUI e também executáveis de linha de comando para tarefas específicas.

## Stack Tecnológica
- Linguagem: Python 3.8+
- GUI: `customtkinter` (baseado em Tkinter) e `Pillow`
- HTTP/Download: `requests`
- Empacotamento: `PyInstaller` via `orchestrator.spec` e `build_exe.bat`
- SO alvo: Windows 10/11 (64‑bit)
- Scripts/Execução: `subprocess`, `ctypes`, `pathlib`, `tempfile`
- Arquivos em lote: `build_exe.bat`, `install_and_run.bat`

Dependências (pip):
- `customtkinter>=5.2.0`, `Pillow>=10.0.0`, `requests>=2.31.0`, `pyinstaller>=6.0.0`
  - Arquivo: `requirements.txt` (raiz) e `nodeecli/requirements.txt` (instalador Node)

Artefatos gerados (PyInstaller):
- `dist/OrquestradorInstalacoes.exe` (GUI principal)
- `dist/install_nodejs.exe` (instalador Node.js – console)
- `dist/vscode_installer.exe` (instalador VS Code – console)

## Convenções do Projeto

### Estilo de Código
- Padrões próximos ao PEP 8 (snake_case para funções/módulos; nomes descritivos).
- Docstrings e mensagens em Português (pt‑BR); logs com emojis/ícones quando conveniente.
- Codificação padrão UTF‑8 para entrada/saída; scripts e testes configuram `PYTHONIOENCODING=utf-8` quando relevante.
- Evitar variáveis de uma letra; priorizar clareza em nomes e mensagens.

### Padrões de Arquitetura
- GUI desacoplada orquestra instaladores externos via `subprocess` em thread dedicada, comunicando com a UI por `queue` (modelo worker + message queue) para manter responsividade.
- Instalação de Node.js via MSI silencioso usando `msiexec /quiet /norestart`, com:
  - detecção de arquitetura (`x64`, `arm64`, `x86`) e fallback controlado (ARM64 → x64);
  - verificação prévia de disponibilidade do artefato e validação de integridade por `SHASUMS256.txt`;
  - suporte a ambientes corporativos: proxy (`--proxy`/variáveis), CA customizada (`--cacert`), opção emergencial `--insecure` (não recomendada);
  - detecção de `nvm-windows` para evitar conflitos;
  - instalação opcional de CLIs globais via `npm` (ex.: `@google/gemini-cli`, `@qwen-code/qwen-code`).
- Instalação do VS Code por download da URL estável oficial (User Installer 64‑bit) com flags silenciosas do Inno Setup para habilitar: ícone desktop, context menu, associações de arquivo e inclusão no `PATH`.
- Empacotamento com `PyInstaller` (spec dedicado para GUI e para cada instalador), ícone via `icon.ico` e UPX habilitado.

Execução e empacotados:
- A GUI detecta modo empacotado (`getattr(sys, 'frozen', False)`) para invocar `install_nodejs.exe` e `vscode_installer.exe` a partir do diretório do aplicativo; em modo script, usa `python <script>.py`.
- Subprocessos em Windows executam com `CREATE_NO_WINDOW` para não abrir consoles.

### Estratégia de Testes
- Scripts de teste manuais focados em execução e codificação/saída:
  - `test_encoding.py` valida encoding UTF‑8 e sintaxe dos scripts.
  - `test_nodejs_installation.py` exercita o fluxo de instalação do Node.js com saídas em tempo real.
- Sem suíte formal de testes automatizados ainda (ex.: pytest). Ao adicionar novas funcionalidades, preferir testes específicos do módulo alterado e cenários de rede simulados (mocks para HTTP e `subprocess`).

Como rodar localmente (dev):
- `pip install -r requirements.txt`
- `python orchestrator_gui.py`
- Para build: `build_exe.bat` (gera `dist/` via `pyinstaller orchestrator.spec --clean`)

### Fluxo de Git
- Branch principal: `main`. Usar branches de feature/fix e PRs pequenos e focados.
- Commits descritivos (português aceito). Opcional: Conventional Commits.
- Para novos recursos, breaking changes ou mudanças arquiteturais, seguir OpenSpec:
  - Criar proposta em `openspec/changes/<change-id>/` (kebab‑case, verbo no início: `add-`, `update-`, `remove-`, `refactor-`).
  - Redigir `proposal.md`, `tasks.md` e deltas de `spec.md` conforme `openspec/AGENTS.md`.
  - Validar com `openspec validate --strict` antes de iniciar implementação.

## Contexto de Domínio
- Provisionamento de estações Windows para desenvolvimento com Node.js e VS Code.
- Ambientes corporativos com proxy/inspeção SSL são comuns; scripts suportam proxy, CA customizada e avisos claros ao desabilitar TLS.
- Requisitos de UX: GUI responsiva, logs em tempo real, progresso e cancelamento.
- Pós‑instalação: garantir `PATH`/`code` disponíveis (reinício de terminal pode ser necessário).

## Restrições Importantes
- Plataforma: Windows 10/11 (64‑bit). Outros SOs não suportados.
- Internet necessária para downloads dos instaladores e checksums.
- Instalação do Node.js MSI pode exigir privilégios de administrador; VS Code User Installer normalmente não.
- Dependência das URLs públicas oficiais (nodejs.org e update.code.visualstudio.com); instabilidade externa pode afetar downloads.
- Em ARM64, fallback para x64 pode ocorrer (emulação) quando pacote nativo não existir.

## Dependências Externas
- Node.js (API/artefatos): `https://nodejs.org/dist/index.json`, `.../vX.Y.Z/SHASUMS256.txt`, `.../node-vX.Y.Z-<arch>.msi`.
- Visual Studio Code (User Installer): `https://update.code.visualstudio.com/latest/win32-x64-user/stable`.
- Ferramentas do sistema: `msiexec.exe`, PowerShell (para ajustar ExecutionPolicy quando aplicável).
- Ecossistema npm (opcional): instalação de CLIs globais pós‑Node.js.

Referências de build/execução:
- `build_exe.bat` (pipeline de build com PyInstaller).
- `orchestrator.spec` (configuração de bundling para GUI e instaladores).
- `install_and_run.bat` (instala dependências e executa a GUI com UTF‑8).

## Estrutura do Repositório
```
Instalacoes/
├── orchestrator_gui.py        # GUI principal (CustomTkinter)
├── orchestrator.spec          # Configuração PyInstaller (GUI + instaladores)
├── build_exe.bat              # Script de build
├── requirements.txt           # Dependências (GUI + build)
├── nodeecli/
│   ├── install_nodejs_refactored.py      # Instalador Node.js (MSI + validação SHA256)
│   ├── README.md              # Docs do instalador Node.js
│   └── requirements.txt       # Dependências específicas
├── vscode/
│   ├── vscode_installer.py    # Instalador VS Code (User Installer + flags)
│   └── README.md              # Docs do instalador VS Code
└── openspec/
    ├── project.md             # Este documento (convenções do projeto)
    └── AGENTS.md              # Guia de uso do OpenSpec
```

## Convenções de Logs e UX
- Logs sempre em UTF‑8 com timestamp `[HH:MM:SS]` na GUI.
- Níveis e cores na GUI: `INFO` (branco), `WARNING` (amarelo), `ERROR` (vermelho), `SUCCESS` (verde).
- Mensagens curtas e acionáveis; evitar quebras multiline desnecessárias.
- Progresso: barra indeterminada no início; muda para determinada com fração concluída por etapa.
- Cancelamento: botão “Cancelar” define `cancel_requested=True` e encerra subprocesso (`terminate` → `kill` de fallback), com mensagens claras.

## Parâmetros de CLI (Instaladores)

Instalador Node.js (`nodeecli/install_nodejs_refactored.py`):
- `--yes` (modo automático, sem confirmações)
- `--track lts|current` ou `--version x.y.z` (seleção de versão)
- `--download-timeout <seg>` e `--install-timeout <seg>`
- `--all-users` (MSI `ALLUSERS=1`)
- `--proxy <url>` | `--cacert <arquivo.crt>` | `--insecure` (rede corporativa)
- `--npm-timeout <seg>` (instalação de CLIs globais)
- `--verbose` e `--log-file <path>`
- Fallback controlado ARM64→x64: `--allow-arch-fallback`

Instalador VS Code (`vscode/vscode_installer.py`):
- Sem prompts; aplica flags silenciosas para: ícone desktop, menus de contexto (arquivos/pastas), associações de arquivo e inclusão no `PATH`.

## Variáveis de Ambiente (rede/execução)
- Proxy: `HTTP_PROXY`/`HTTPS_PROXY` reconhecidos pela `requests`.
- Certificados: `REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE` podem ser usados como alternativa a `--cacert`.
- Windows: GUI configura High‑DPI via `ctypes`; subprocessos com `CREATE_NO_WINDOW`.

## Práticas de Código
- PEP 8 (snake_case), nomes descritivos, sem variáveis de uma letra.
- UI e logs em pt‑BR; exceptions transformadas em mensagens de log amigáveis.
- Detectar `sys.frozen` para paths; usar `Path`/`os.path` ao resolver recursos.
- Evitar I/O bloqueante na thread da GUI; usar fila (`queue.Queue`) para mensagens thread‑safe.
