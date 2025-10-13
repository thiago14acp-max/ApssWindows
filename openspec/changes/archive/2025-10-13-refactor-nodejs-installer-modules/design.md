## Contexto
O arquivo `nodeecli/install_nodejs.py` original (agora removido) continha mais de 1500 linhas de código com múltiplas responsabilidades: instalação do Node.js, instalação do Gemini CLI e instalação do Qwen CLI. Esta estrutura monolítica dificultava a manutenção, testabilidade e reutilização do código.

## Goals / Non-Goals
- Goals:
  - Modularizar o código em componentes reutilizáveis
  - Melhorar a manutenibilidade e testabilidade
  - Preservar toda a funcionalidade existente
  - Manter compatibilidade com a interface de linha de comando
- Non-Goals:
  - Alterar o comportamento funcional do instalador
  - Modificar a interface de linha de comando
  - Quebrar a compatibilidade com scripts existentes

## Decisions
- Decision: Criar módulos separados para cada responsabilidade principal
  - **Rational**: Separação clara de responsabilidades facilita manutenção e testes
  - **Alternatives considered**: Manter código monolítico com refatoração interna
- Decision: Criar módulo `common.py` para funcionalidades compartilhadas
  - **Rational**: Evita duplicação de código entre os instaladores
  - **Alternatives considered**: Repetir código em cada módulo
- Decision: Manter arquivo `install_nodejs_refactored.py` como ponto de entrada principal
  - **Rational**: Preserva compatibilidade com uso existente
  - **Alternatives considerados**: Exigir uso direto dos módulos

## Risks / Trade-offs
- **Risk**: Complexidade adicional na estrutura de diretórios
  - **Mitigation**: Documentação clara e exemplos de uso
- **Risk**: Possíveis problemas de importação em ambientes restritos
  - **Mitigation**: Testes de importação e validação de sintaxe
- **Trade-off**: Mais arquivos para gerenciar vs código mais organizado
  - **Justification**: Benefícios de manutenibilidade superam a complexidade adicional

## Migration Plan
1. **Fase 1**: Implementar módulos em paralelo com código original
2. **Fase 2**: Testar extensively a versão modularizada
3. **Fase 3**: Atualizar documentação e exemplos
4. **Fase 4**: Substituir gradualmente o uso do arquivo original
5. **Fase 5**: Considerar remoção do arquivo original após período de transição

## Open Questions
- Deve o arquivo original ser mantido por compatibilidade ou removido após transição?
- Como lidar com empacotamento PyInstaller com a nova estrutura?
- É necessário criar testes unitários mais abrangentes para cada módulo?

## Estrutura Final
```
nodeecli/
├── install_nodejs_refactored.py   # Versão modularizada (ponto de entrada)
├── test_modular.py                # Script de teste para validação
├── README.md                      # Documentação atualizada
└── modules/                       # Módulos da versão modularizada
    ├── __init__.py                # Inicialização do pacote
    ├── common.py                  # Funcionalidades compartilhadas
    ├── nodejs_installer.py        # Instalador do Node.js
    ├── gemini_cli_installer.py    # Instalador do Gemini CLI
    └── qwen_cli_installer.py      # Instalador do Qwen CLI
```

## Validação
- Testes de importação bem-sucedidos para todos os módulos
- Script refatorado compilado sem erros
- Interface de linha de comando preservada
- Funcionalidades básicas testadas e validadas
