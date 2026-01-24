# Antigravity IDE Installer

Módulo de instalação automatizada do **Google Antigravity IDE** — um fork do VS Code com integração nativa do Gemini AI.

## Status

✅ **Implementado** — pronto para uso.

## O que é Antigravity?

Antigravity é uma IDE "agent-first" desenvolvida pelo Google, baseada no VS Code, com as seguintes características:

- 🤖 **Integração nativa com Gemini AI** — assistente de código integrado
- 🔄 **Agentes autônomos** — podem planejar, codificar e testar automaticamente
- 🌐 **Navegação web integrada** — agentes podem navegar para pesquisar documentação
- 🛠️ **Baseado no VS Code** — familiar para desenvolvedores

## Requisitos

- **Windows 10 ou superior**
- **4GB RAM** (8GB recomendado)
- **500MB de espaço em disco**
- **Conexão com internet**
- **Conta Google pessoal** (Workspace não suportado no preview)

## Uso

### Via Python

```python
from antigravity import installer

# Executa a instalação completa
installer.install()
```

### Via Linha de Comando

```bash
python -m antigravity.installer
```

### Standalone

```bash
python antigravity/installer.py
```

## Arquiteturas Suportadas

| Arquitetura | Suporte |
|-------------|---------|
| x64 (AMD64) | ✅ |
| ARM64       | ✅ |

O instalador detecta automaticamente a arquitetura do sistema.

## Opções de Instalação

O instalador configura automaticamente:

- ✅ Ícone na área de trabalho
- ✅ Menu de contexto para arquivos
- ✅ Menu de contexto para pastas
- ✅ Adiciona ao PATH do sistema

## Após a Instalação

1. Abra o Antigravity
2. Faça login com sua **conta Google pessoal**
3. Comece a codificar com assistência de IA!

## Dependências

- `requests` — para download do instalador

## Links Úteis

- [Site Oficial](https://antigravity.google/)
- [Página de Download](https://antigravity.google/download)
