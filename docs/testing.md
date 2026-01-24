# 🧪 Testes

## Estrutura

```
tests/
├── integration/
│   ├── test_nodejs_installation.py
│   └── test_encoding.py
└── nodeecli/
    └── test_modular.py
```

---

## Comandos

### Testes de Integração

```bash
python -m tests.integration.test_nodejs_installation
python -m tests.integration.test_encoding
```

### Testes Modulares

```bash
python -m tests.nodeecli.test_modular
```

---

## Instalação Completa

> [!NOTE]
> Por padrão, testes executam apenas validação. Para instalação real, defina a variável de ambiente.

```bash
# Windows
set RUN_INSTALLATION_TESTS=1 && python -m tests.integration.test_nodejs_installation
```

---

[← Voltar ao índice](README.md)
