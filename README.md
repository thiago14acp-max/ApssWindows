# 🚀 Orquestrador de Instalações

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)]()

> 🖥️ Aplicação GUI para automatizar a instalação de ferramentas de desenvolvimento no Windows

## 📋 Sobre o Projeto

O Orquestrador de Instalações é uma ferramenta desenvolvida para simplificar e automatizar o processo de instalação de ferramentas essenciais de desenvolvimento em ambientes Windows. Com uma interface intuitiva e moderna, este aplicativo permite instalar Node.js, VS Code e outras ferramentas com apenas alguns cliques, eliminando a necessidade de downloads manuais e configurações complexas. A versão mais recente inclui suporte para instalação de CLIs avançados como Google Gemini e Qwen Code, além de recursos avançados de verificação e segurança.

## ✨ Recursos

- 🎨 Interface gráfica moderna com CustomTkinter
- 📦 Instalação automatizada de Node.js + CLI Tools (npm, npx)
- 💻 Instalação automatizada de Visual Studio Code
- 🤖 Instalação de CLIs adicionais (Google Gemini, Qwen Code)
- 📊 Console de logs em tempo real com coloração por nível
- 📈 Barra de progresso com status detalhado
- 🌓 Suporte a temas (System/Light/Dark)
- ⚙️ Configurações personalizáveis (timeouts, modo automático)
- ❌ Cancelamento de instalações em andamento
- 🪟 Compatibilidade com Windows 10 e 11
- 🔍 Suporte a High-DPI
- 🔐 Verificação de integridade com checksums SHA256
- 🌐 Suporte a proxy corporativo e certificados personalizados
- 🏗️ Arquitetura modular para fácil manutenção e extensibilidade
- 📋 Detecção e aviso de conflitos com nvm-windows
- 💾 Atualização automática do Node.js (se já instalado)
- 📥 Download com barra de progresso e fallback de arquitetura ARM64 para x64

## 📋 Requisitos

### 🖥️ Requisitos do Sistema:
- Windows 10 ou 11 (64-bit)
- Python 3.8+ (para execução via código-fonte)
- 🌐 Conexão com internet (para downloads)
- 🔐 Permissões de administrador (recomendado para instalações)

## 🛠️ Instalação

### 🎯 Opção 1: Usando o executável (recomendado para usuários finais):
1. 📥 Baixe a versão mais recente da página de releases
2. 📂 Extraia o arquivo ZIP
3. ▶️ Execute `OrquestradorInstalacoes.exe`
4. ✅ Não é necessário instalar o Python

### 👨‍💻 Opção 2: Executando a partir do código-fonte (para desenvolvedores):
1. 📋 Clone o repositório
2. 📁 Navegue até o diretório `Instalacoes/`
3. 📦 Instale as dependências: `pip install -r requirements.txt`
4. ▶️ Execute: `python orchestrator_gui.py`

## 🎮 Uso

### 🎯 Uso Básico:
1. ▶️ Inicie a aplicação
2. ☑️ Selecione as ferramentas para instalar (Node.js, VS Code, e/ou CLIs adicionais)
3. ⚙️ Configure as configurações (opcional):
   - 🤖 Habilite "Modo Automático" para instalação não assistida
   - ⏱️ Ajuste os valores de timeout, se necessário
   - 🌐 Configure proxy se necessário
4. 🚀 Clique em "Iniciar Instalação"
5. 👀 Monitore o progresso na área do console
6. ✅ Aguarde a mensagem de conclusão

### 🔧 Configurações Avançadas:
- **🤖 Modo Automático (--yes)**: Ignora prompts de confirmação no instalador Node.js
- **⏱️ Timeout de Download**: Tempo máximo (segundos) para esperar downloads (padrão: 30)
- **⏱️ Timeout de Instalação**: Tempo máximo (segundos) para esperar instalações (padrão: 600)
- **🎨 Tema da Interface**: Escolha entre os temas System, Light ou Dark
- **🌐 Proxy**: Configurar proxy para requisições HTTP/HTTPS
- **🔒 Certificados**: Usar certificado CA personalizado ou desativar verificação SSL (não recomendado)

### ❌ Cancelando Instalações:
- 🛑 Clique no botão "Cancelar" durante a instalação
- ⏹️ O processo atual será encerrado gracefulmente
- 🧹 Instalações parciais podem precisar de limpeza manual

## 🔨 Compilando a Partir do Código-Fonte

### 📋 Pré-requisitos:
- Python 3.8 ou superior instalado
- Todas as dependências instaladas: `pip install -r requirements.txt`

### 🏗️ Passos de Compilação:
1. ✅ Certifique-se de que `icon.ico` existe no diretório raiz
2. 🔨 Execute o script de build: `build_exe.bat` (Windows)
3. 🔨 Ou manualmente: `pyinstaller orchestrator.spec --clean`
4. 📁 Os executáveis estarão em `dist/`:
   - `OrquestradorInstalacoes.exe` (Interface Gráfica)
   - `install_nodejs.exe` (Instalador Node.js)
   - `vscode_installer.exe` (Instalador VS Code)

### ⚙️ Opções de Build:
- 📁 Modo one-directory (padrão): Inicialização mais rápida, múltiplos arquivos
- 📄 Modo one-file: Edite `orchestrator.spec` e defina `onefile=True` na seção EXE

## 🔧 Solução de Problemas

### 💡 Problemas Comuns:

#### ❌ Erro "CustomTkinter não está instalado":
- **🔧 Solução**: Instale as dependências com `pip install -r requirements.txt`

#### ❌ Erro "Script não encontrado":
- **🔧 Solução**: Certifique-se de que `nodeecli/install_nodejs_refactored.py` e `vscode/vscode_installer.py` existem
- **🔧 Para o executável**: Verifique se os executáveis `install_nodejs.exe` e `vscode_installer.exe` existem na pasta `dist`

#### ❌ Instalação falha com timeout:
- **🔧 Solução**: Aumente os valores de timeout nas configurações
- **🌐 Verifique a conexão com a internet**
- **⏰ Tente novamente mais tarde (o servidor pode estar temporariamente indisponível)**

#### ❌ Problemas de exibição em High-DPI:
- **🔧 Solução**: A aplicação lida automaticamente com High-DPI no Windows 10/11
- **🖥️ Se os problemas persistirem, tente alterar as configurações de escala de exibição do Windows**

#### ❌ Executável não inicia:
- **🔧 Solução**: Verifique o Windows Defender ou antivírus (pode bloquear executáveis não assinados)
- **👤 Execute como administrador se ocorrerem erros de permissão**
- **📁 Verifique a pasta `%TEMP%` quanto a erros de extração do PyInstaller**
- **✅ Certifique-se de que todos os três executáveis estão presentes na pasta `dist`**

#### ❌ Conflito com nvm-windows detectado:
- **🔧 Solução**: O instalador detecta automaticamente se o nvm-windows está instalado e alerta sobre possíveis conflitos
- **📝 Recomendação**: Use o nvm-windows para gerenciar versões do Node.js se já estiver instalado

## 📁 Estrutura do Projeto

```
Instalacoes/
├── orchestrator_gui.py       # 🖥️ Aplicação GUI principal
├── orchestrator.spec          # ⚙️ Configuração do PyInstaller
├── build_exe.bat              # 🔨 Script de automação de build
├── requirements.txt           # 📦 Dependências Python
├── icon.ico                   # 🎨 Ícone da aplicação
├── README.md                  # 📖 Este arquivo
├── nodeecli/
│   ├── install_nodejs_refactored.py  # 📦 Script de instalação do Node.js (modular)
│   ├── requirements.txt       # 📋 Dependências do instalador Node.js
│   ├── README.md              # 📖 Documentação do instalador Node.js
│   └── modules/               # 🧩 Módulos da versão modularizada
│       ├── __init__.py        # Inicialização do pacote
│       ├── common.py          # Funcionalidades compartilhadas
│       ├── nodejs_installer.py # Instalador do Node.js
│       ├── gemini_cli_installer.py # Instalador do Gemini CLI
│       └── qwen_cli_installer.py # Instalador do Qwen CLI
└── vscode/
    ├── vscode_installer.py    # 💻 Script de instalação do VS Code
    └── README.md              # 📖 Documentação do instalador VS Code
```

## 🧩 Detalhes Técnicos

### 🏗️ Arquitetura:
- **🎨 Framework GUI**: CustomTkinter (wrapper moderno do tkinter)
- **🧵 Threading**: Threads em segundo plano para execução de subprocessos
- **📡 IPC**: Passação de mensagens baseada em fila para atualizações thread-safe da GUI
- **⚙️ Gerenciamento de Subprocessos**: Módulo `subprocess` do Python com captura de saída em tempo real
- **📦 Modularização**: Código organizado em módulos independentes para fácil manutenção

### 🔧 Componentes Chave:
- **📱 Classe `OrchestratorApp`**: Janela principal da aplicação e lógica
- **🚀 `start_installation()`**: Inicia o processo de instalação
- **👷 `run_installations()`**: Thread worker que executa os scripts de instalação
- **📜 `run_script()`**: Wrapper de subprocess com captura de saída
- **📨 `process_queue()`**: Processador de mensagens da thread da GUI
- **🛑 `cancel_installation()`**: Terminação graceful de processos
- **🔍 `NodejsInstaller`**: Classe responsável pela instalação do Node.js
- **🤖 `GeminiCliInstaller`**: Classe responsável pela instalação do Gemini CLI
- **🤖 `QwenCliInstaller`**: Classe responsável pela instalação do Qwen CLI

### 🛡️ Recursos de Segurança e Verificação:
- **✅ Verificação SHA256**: Todos os downloads são verificados com checksums oficiais
- **🌐 Suporte a Proxy**: Configuração de proxy para ambientes corporativos
- **🔒 Certificados Personalizados**: Suporte a CA personalizada para ambientes com certificados corporativos
- **⚠️ Detecção de Conflitos**: Verificação de nvm-windows e alerta de possíveis conflitos


## 📞 Contato/Suporte

### 🆘 Como obter ajuda:
- 🐛 [Reportar problemas](https://github.com/ssmvictor/ApssWindows/issues) - Para bugs e problemas
- 💬 [Discussões](https://github.com/ssmvictor/ApssWindows/discussions) - Para dúvidas e sugestões
- 📖 [Documentação](https://github.com/ssmvictor/ApssWindows/wiki) - Para guias detalhados

### 🤝 Contribuição:
Contribuições são bem-vindas! Por favor, leia nosso [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre nosso código de conduta e o processo para enviar pull requests.

---

<div align="center">
  <p>Feito com ❤️ </p>
  <p>
    <a href="#top">Voltar ao topo</a>
  </p>
</div>
