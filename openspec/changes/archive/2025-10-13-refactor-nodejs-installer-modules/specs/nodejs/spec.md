## ADDED Requirements
### Requirement: Módulo de Instalação do Node.js
O sistema SHALL fornecer um módulo dedicado para instalação do Node.js que encapsule toda a lógica de detecção, download e instalação.

#### Scenario: Instalação do Node.js via módulo
- **WHEN** o módulo nodejs_installer é invocado com parâmetros válidos
- **THEN** o sistema SHALL detectar a arquitetura do sistema
- **AND** o sistema SHALL baixar o instalador apropriado
- **AND** o sistema SHALL validar a integridade do arquivo
- **AND** o sistema SHALL executar a instalação silenciosa
- **AND** o sistema SHALL retornar o status da instalação

### Requirement: Módulo de Instalação do Gemini CLI
O sistema SHALL fornecer um módulo dedicado para instalação do Gemini CLI que possa ser utilizado independentemente ou como parte do fluxo principal.

#### Scenario: Instalação do Gemini CLI via módulo
- **WHEN** o módulo gemini_cli_installer é invocado
- **THEN** o sistema SHALL verificar se o Node.js está instalado
- **AND** o sistema SHALL instalar o pacote @google/gemini-cli globalmente
- **AND** o sistema SHALL verificar se o comando gemini está disponível
- **AND** o sistema SHALL fornecer feedback sobre o resultado

### Requirement: Módulo de Instalação do Qwen CLI
O sistema SHALL fornecer um módulo dedicado para instalação do Qwen CLI que possa ser utilizado independentemente ou como parte do fluxo principal.

#### Scenario: Instalação do Qwen CLI via módulo
- **WHEN** o módulo qwen_cli_installer é invocado
- **THEN** o sistema SHALL verificar se o Node.js está instalado
- **AND** o sistema SHALL instalar o pacote @qwen-code/qwen-code globalmente
- **AND** o sistema SHALL verificar se o comando qwen está disponível
- **AND** o sistema SHALL fornecer feedback sobre o resultado

### Requirement: Módulo de Funcionalidades Comuns
O sistema SHALL fornecer um módulo com funcionalidades compartilhadas entre os instaladores para evitar duplicação de código.

#### Scenario: Uso de funcionalidades comuns
- **WHEN** qualquer módulo de instalador precisa de logging
- **THEN** o sistema SHALL usar a classe Logger do módulo common
- **AND** quando precisar detectar arquitetura
- **THEN** o sistema SHALL usar a função detectar_arquitetura do módulo common
- **AND** quando precisar verificar permissões
- **THEN** o sistema SHALL usar a função verificar_permissoes_admin do módulo common

## MODIFIED Requirements
### Requirement: Instalador Principal do Node.js
O instalador principal SHALL ser refatorado para usar os novos módulos mantendo a mesma interface de linha de comando e comportamento.

#### Scenario: Execução do instalador principal
- **WHEN** o usuário executa install_nodejs_refactored.py com qualquer parâmetro suportado
- **THEN** o sistema SHALL invocar os módulos apropriados
- **AND** o sistema SHALL manter a mesma saída e comportamento
- **AND** o sistema SHALL suportar todos os parâmetros existentes
- **AND** o sistema SHALL preservar todos os códigos de retorno
