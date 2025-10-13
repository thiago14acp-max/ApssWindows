## Why
O arquivo `nodeecli/install_nodejs.py` original (removido em limpeza posterior) continha mais de 1500 linhas de código com múltiplas responsabilidades: instalação do Node.js, instalação do Gemini CLI e instalação do Qwen CLI. Esta estrutura monolítica dificultava a manutenção, testabilidade e reutilização do código. A modularização permitirá melhor organização, testes independentes e reutilização dos componentes em outros contextos.

## What Changes
- **BREAKING**: Refatorar o arquivo `install_nodejs.py` para usar módulos separados (ponto de entrada passa a ser `install_nodejs_refactored.py`)
- Criar módulo `nodejs_installer.py` para funcionalidades de instalação do Node.js
- Criar módulo `gemini_cli_installer.py` para instalação do Gemini CLI
- Criar módulo `qwen_cli_installer.py` para instalação do Qwen CLI
- Criar módulo `common.py` para funcionalidades compartilhadas (logging, detecção de arquitetura, etc.)
- Manter a interface de linha de comando existente no arquivo `install_nodejs_refactored.py`
- Preservar toda a funcionalidade existente sem alterações comportamentais

## Impact
- Affected specs: nodejs-installation
- Affected code: nodeecli/install_nodejs_refactored.py (refatoração completa)
- New modules: nodeecli/modules/nodejs_installer.py, nodeecli/modules/gemini_cli_installer.py, nodeecli/modules/qwen_cli_installer.py, nodeecli/modules/common.py
- Build: Atualizar o arquivo `orchestrator.spec` para incluir os novos módulos no empacotamento
