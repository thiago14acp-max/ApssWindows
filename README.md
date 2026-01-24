# Orquestrador de Instalações

Aplicação desktop Windows para instalação automatizada de ferramentas de desenvolvimento.

## Quick Start

```bash
# Clone e execute
git clone <url-do-repositorio>
cd <nome-do-repositorio>

# Opção 1: Script automatizado
install_and_run.bat

# Opção 2: Manual
pip install -r requirements.txt
python srcmain.py
```

## Ferramentas Suportadas

| Ferramenta | Descrição |
|------------|-----------|
| **Node.js** | Runtime + CLI Tools |
| **VS Code** | Editor de código |
| **Git** | Controle de versão |
| **MCP Excel** | Server para Excel |
| **Antigravity** | Gemini CLI *(em desenvolvimento)* |
| **OpenCode** | OpenCode CLI *(em desenvolvimento)* |

## Documentação

- [Arquitetura](docs/architecture.md) — Estrutura do projeto e componentes
- [Testes](docs/testing.md) — Como executar os testes
- [Build](docs/build.md) — Gerar executáveis

## Requisitos

- Windows 10+
- Python 3.7+
