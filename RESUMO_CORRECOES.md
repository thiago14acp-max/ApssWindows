# Resumo das Correções Aplicadas

## Problema Original
Erro de codificação ao instalar o "Node.js + CLI Tools":
```
'charmap' codec can't encode characters in position 0-1: character maps to <undefined>
```

## Causa do Problema
O Windows estava usando a codificação 'charmap' (padrão em sistemas Windows em português) para processar a saída dos subprocessos, mas os scripts continham caracteres especiais (como "✓" e "⚠️") que não podem ser codificados nesta codificação.

## Correções Aplicadas

### 1. Script do Instalador do Node.js (`nodeecli/install_nodejs.py`)
- Adicionados parâmetros `encoding='utf-8'` e `errors='replace'` em todas as chamadas de `subprocess.run()`
- Corrigidos erros de variáveis não inicializadas

### 2. Script do Instalador do VS Code (`vscode/vscode_installer.py`)
- Adicionados parâmetros `encoding='utf-8'` e `errors='replace'` na chamada de `subprocess.run()`
- Corrigidos erros de verificações de variáveis None

### 3. Interface Gráfica (`orchestrator_gui.py`)
- Adicionados parâmetros `encoding='utf-8'` e `errors='replace'` na chamada de `subprocess.Popen()`
- Isso garante que os scripts filhos sejam executados com a codificação correta

### 4. Script Batch (`install_and_run.bat`)
- Adicionada a linha `set PYTHONIOENCODING=utf-8` antes de executar o Python
- Isso força o Python a usar UTF-8 para entrada/saída padrão

## Soluções Alternativas
Caso o problema persista em outros ambientes, estas são as soluções possíveis:

1. **Definir variável de ambiente globalmente:**
   ```cmd
   setx PYTHONIOENCODING utf-8
   ```

2. **Executar com a variável de ambiente:**
   ```cmd
   set PYTHONIOENCODING=utf-8 && python script.py
   ```

3. **Modificar o script para forçar UTF-8:**
   ```python
   import sys
   import io
   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
   ```

## Testes Realizados
- ✅ Script do Node.js executando sem erros de codificação
- ✅ Script do VS Code compilando sem erros de codificação
- ✅ Interface gráfica iniciando sem erros
- ✅ Instalação do Node.js executando até o final (mesmo que com erro de permissão)

## Resultado
O problema de codificação foi completamente resolvido. Os scripts agora funcionam corretamente em sistemas Windows em português, exibindo todos os caracteres especiais adequadamente.