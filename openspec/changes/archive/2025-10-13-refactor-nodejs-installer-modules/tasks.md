## 1. Preparação
- [x] 1.1 Criar estrutura de diretórios para os módulos
- [x] 1.2 Criar proposta OpenSpec para a modularização
- [x] 1.3 Criar arquivo de especificação para a proposta

## 2. Criação dos Módulos
- [x] 2.1 Criar módulo common.py com funcionalidades compartilhadas
- [x] 2.2 Criar módulo nodejs_installer.py
- [x] 2.3 Criar módulo gemini_cli_installer.py
- [x] 2.4 Criar módulo qwen_cli_installer.py

## 3. Refatoração
- [x] 3.1 Refatorar install_nodejs.py para usar os novos módulos (ponto de entrada atualizado para install_nodejs_refactored.py)
- [x] 3.2 Garantir compatibilidade com interface de linha de comando existente
- [x] 3.3 Atualizar imports e dependências

## 4. Testes e Validação
- [x] 4.1 Testar importação de todos os módulos
- [x] 4.2 Testar compilação do script refatorado
- [x] 4.3 Testar interface de linha de comando
- [x] 4.4 Validar que toda funcionalidade existente foi preservada

## 5. Documentação e Build
- [x] 5.1 Atualizar documentação dos módulos
- [x] 5.2 Criar script de teste para validação
- [x] 5.3 Criar design.md com decisões técnicas
