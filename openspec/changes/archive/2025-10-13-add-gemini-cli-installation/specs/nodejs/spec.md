## ADDED Requirements
### Requirement: Confirmação de Instalação do Gemini CLI
O sistema SHALL fornecer confirmação clara da instalação do pacote @google/gemini-cli durante o processo de instalação do Node.js + CLI Tools.

#### Scenario: Instalação bem-sucedida do Gemini CLI
- **WHEN** o pacote @google/gemini-cli é instalado com sucesso via npm install -g
- **THEN** o sistema SHALL exibir mensagem de sucesso no log
- **AND** o sistema SHALL verificar que o comando gemini está disponível no PATH
- **AND** o sistema SHALL exibir informações básicas sobre como usar o Gemini CLI

#### Scenario: Falha na instalação do Gemini CLI
- **WHEN** ocorre erro durante a instalação do @google/gemini-cli
- **THEN** o sistema SHALL exibir mensagem de erro clara no log
- **AND** o sistema SHALL fornecer instruções para instalação manual
- **AND** o sistema SHALL continuar o processo de instalação sem interromper

## MODIFIED Requirements
### Requirement: Instalação de Ferramentas CLI Adicionais
O instalador do Node.js SHALL instalar automaticamente ferramentas CLI adicionais após a conclusão da instalação do Node.js.

#### Scenario: Pós-instalação do Node.js
- **WHEN** a instalação do Node.js é concluída com sucesso
- **THEN** o sistema SHALL instalar o pacote @google/gemini-cli globalmente via npm
- **AND** o sistema SHALL verificar se a instalação foi bem-sucedida
- **AND** o sistema SHALL exibir no log o status da instalação do Gemini CLI
- **AND** o sistema SHALL fornecer feedback claro sobre o resultado da instalação