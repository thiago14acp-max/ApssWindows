# Instalador Node.js para Windows - Versão Modularizada

Este projeto contém uma versão modularizada do instalador automático do Node.js para Windows, que permite instalar o Node.js, Gemini CLI e Qwen CLI de forma independente ou conjunta.

## Estrutura do Projeto

```
nodeecli/
├── install_nodejs_refactored.py   # Versão modularizada (ponto de entrada)
├── requirements.txt               # Dependências Python
├── README.md                      # Este arquivo
└── modules/                       # Módulos da versão modularizada
    ├── __init__.py                # Inicialização do pacote
    ├── common.py                  # Funcionalidades compartilhadas
    ├── nodejs_installer.py        # Instalador do Node.js
    ├── gemini_cli_installer.py    # Instalador do Gemini CLI
    └── qwen_cli_installer.py      # Instalador do Qwen CLI
```

## Módulos

### common.py
Contém funcionalidades compartilhadas entre os instaladores:
- Sistema de logging
- Detecção de arquitetura do sistema
- Verificação de permissões de administrador
- Configuração de políticas de execução do PowerShell
- Preparação de ambiente com caminhos do Node.js

### nodejs_installer.py
Encapsula toda a lógica de instalação do Node.js:
- Verificação de versão instalada
- Download do instalador MSI
- Validação de integridade SHA256
- Instalação silenciosa via msiexec
- Suporte a proxy e certificados personalizados

### gemini_cli_installer.py
Responsável pela instalação do Gemini CLI:
- Verificação de pré-requisitos (Node.js/npm)
- Instalação do pacote @google/gemini-cli
- Validação pós-instalação
- Informações de uso

### qwen_cli_installer.py
Responsável pela instalação do Qwen CLI:
- Verificação de pré-requisitos (Node.js/npm)
- Instalação do pacote @qwen-code/qwen-code
- Validação pós-instalação
- Informações de uso

## Uso

### Via install_nodejs_refactored.py (Recomendado)

```bash
# Instalação interativa padrão
python install_nodejs_refactored.py

# Modo automático (sem prompts)
python install_nodejs_refactored.py -y

# Instalar versão específica do Node.js
python install_nodejs_refactored.py --version 18.19.0

# Usar proxy
python install_nodejs_refactored.py --proxy http://proxy.empresa.com:8080

# Instalar para todos os usuários
python install_nodejs_refactored.py --all-users

# Verbose com arquivo de log
python install_nodejs_refactored.py --verbose --log-file install.log
```

### Via Módulos Individuais

```python
from modules.nodejs_installer import NodejsInstaller
from modules.gemini_cli_installer import GeminiCliInstaller
from modules.qwen_cli_installer import QwenCliInstaller
from modules.common import Logger

# Inicializar logger
logger = Logger(verbose=True)

# Instalar Node.js
nodejs_installer = NodejsInstaller(logger)
sucesso, versao = nodejs_installer.instalar()

# Instalar Gemini CLI
gemini_installer = GeminiCliInstaller(logger)
gemini_sucesso = gemini_installer.instalar()

# Instalar Qwen CLI
qwen_installer = QwenCliInstaller(logger)
qwen_sucesso = qwen_installer.instalar()
```

## Requisitos

- Python 3.7 ou superior
- Biblioteca requests: `pip install requests`
- Windows 10/11 (64-bit recomendado)
- Permissões de administrador (recomendado)
- Conexão com internet

## Vantagens da Modularização

1. **Manutenibilidade**: Código organizado em módulos com responsabilidades claras
2. **Reutilização**: Cada instalador pode ser usado independentemente
3. **Testabilidade**: Módulos podem ser testados isoladamente
4. **Extensibilidade**: Fácil adicionar novos instaladores de ferramentas
5. **Clareza**: Código mais limpo e fácil de entender

## Parâmetros de Linha de Comando

- `-y, --yes`: Prosseguir sem prompts interativos
- `--proxy URL`: Configurar proxy para requisições HTTP/HTTPS
- `--version VERSAO`: Instalar versão específica do Node.js
- `--track {lts,current}`: Escolher trilha de lançamento (padrão: lts)
- `--install-timeout SEG`: Timeout para instalação do MSI (padrão: 300)
- `--all-users`: Instalar para todos os usuários
- `--download-timeout SEG`: Timeout para downloads (padrão: 300)
- `--verbose`: Aumentar verbosidade dos logs
- `--log-file ARQUIVO`: Salvar logs em arquivo
- `--allow-arch-fallback`: Permitir fallback automático de ARM64 para x64
- `--npm-timeout SEG`: Timeout para instalação de pacotes npm (padrão: 300)
- `--cacert ARQUIVO`: Usar certificado CA personalizado
- `--insecure`: Desativar verificação de certificado SSL/TLS (não recomendado)

## Migração da Versão Original

Observação: a versão monolítica (`install_nodejs.py`) foi removida.
Para migrar para a versão modularizada:

1. Substitua o uso de `install_nodejs.py` por `install_nodejs_refactored.py`
2. A interface de linha de comando é idêntica, não há necessidade de alterar scripts existentes
3. Se usar como módulo Python, atualize os imports para usar os novos módulos

## Suporte

Para problemas ou sugestões:
1. Verifique os logs de erro para detalhes
2. Certifique-se de estar executando como administrador
3. Verifique sua conexão com a internet
4. Em ambientes corporativos, verifique configurações de proxy e firewall
