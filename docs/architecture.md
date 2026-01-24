# 🏗️ Arquitetura

## Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│               (Ponto de entrada)                        │
└─────────────────────┬───────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────┐      ┌──────────────────────┐
│    MainView     │◄────►│   OrchestratorApp    │
│   (UI Layer)    │      │  (App Layer)         │
└─────────────────┘      └──────────┬───────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │ InstallationService  │
                        │   (Core Layer)       │
                        └──────────┬───────────┘
                                   │
         ┌─────────────┬───────────┼───────────┬─────────────┐
         ▼             ▼           ▼           ▼             ▼
     nodeecli/     vscode/       git/     mcp_excel/    antigravity/
```

---

## Estrutura de Diretórios

```
src/
├── main.py              # Ponto de entrada
├── app/
│   ├── orchestrator.py  # Coordenador central
│   └── app_state.py     # Estado da aplicação
├── core/
│   └── installation_service.py
└── ui/
    └── main_view.py     # Interface CustomTkinter
```

---

## Camadas

### 🎨 UI Layer

**MainView** — Janela CustomTkinter com sidebar, console de logs e barra de progresso.

### ⚙️ App Layer

**OrchestratorApp** — Gerencia eventos, coordena UI ↔ Service.

**AppState** — Variáveis reativas (checkboxes, flags).

### 🔧 Core Layer

**InstallationService** — Executa instalações em subprocess com comunicação via Queue.

---

## Módulos

| Módulo | Descrição | Status |
|--------|-----------|--------|
| `nodeecli/` | Node.js + CLI Tools | ✅ |
| `vscode/` | Visual Studio Code | ✅ |
| `git/` | Git for Windows | ✅ |
| `mcp_excel/` | MCP Excel Server | ✅ |
| `antigravity/` | Gemini CLI | 🚧 |
| `opencode/` | OpenCode CLI | 🚧 |

---

## Fluxo de Comunicação

```
┌────────────┐    eventos    ┌──────────────┐    Queue     ┌───────────────────┐
│  MainView  │◄─────────────►│ Orchestrator │◄────────────►│InstallationService│
└────────────┘               └──────────────┘              └───────────────────┘
```

**Mensagens**: `LOG`, `PROGRESS`, `COMPLETE`

---

[← Voltar ao índice](README.md)
