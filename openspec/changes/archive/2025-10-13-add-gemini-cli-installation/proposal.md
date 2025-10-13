## Why
O instalador atual do Node.js + CLI Tools não está verificando corretamente se o pacote @google/gemini-cli foi instalado. O log mostra que o Node.js foi instalado com sucesso, mas não há confirmação da instalação do Gemini CLI, causando incerteza para o usuário sobre se a ferramenta foi realmente instalada.

## What Changes
- Adicionar verificação explícita no log para confirmar a instalação do @google/gemini-cli
- Melhorar o feedback visual no processo de instalação para indicar sucesso ou falha na instalação do CLI
- Garantir que o log mostre claramente quando o Gemini CLI é instalado com sucesso
- Adicionar mensagem informativa sobre como usar o Gemini CLI após a instalação

## Impact
- Affected specs: nodejs-installation
- Affected code: nodeecli/install_nodejs_refactored.py (função instalar_gemini_cli e função main)
