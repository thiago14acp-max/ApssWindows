# Orquestrador de Instalações

Uma aplicação de desktop para Windows que facilita a instalação de ferramentas de desenvolvimento como Node.js, Visual Studio Code e CLIs.

## Funcionalidades

- **Interface Gráfica Amigável**: Gerencie as instalações de forma visual e intuitiva.
- **Instalação Automatizada**: Instala Node.js e ferramentas de linha de comando com um clique.
- **Verificação de Dependências**: Garante que o ambiente esteja pronto para a instalação.
- **Logs Detalhados**: Acompanhe o progresso da instalação em tempo real.
- **Temas**: Suporte a temas claro, escuro e de sistema.

## Como Usar

### Pré-requisitos

- **Windows 10 ou superior**
- **Python 3.7 ou superior**

### Execução

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Execute o script de inicialização:**
    - Dê um duplo clique no arquivo `install_and_run.bat`.
    - O script irá instalar as dependências necessárias e iniciar a aplicação.

    Como alternativa, você pode executar manualmente:
    ```bash
    pip install -r requirements.txt
    python src/main.py
    ```

## Estrutura do Projeto

- **`src/`**: Contém o código-fonte da aplicação.
  - **`app/`**: Lógica de orquestração e estado da aplicação.
  - **`core/`**: Serviços de back-end, como o `InstallationService`.
  - **`ui/`**: Componentes da interface gráfica.
  - **`main.py`**: Ponto de entrada da aplicação.
- **`nodeecli/`**: Scripts e módulos para a instalação do Node.js e CLIs.
- **`vscode/`**: Scripts para a instalação do Visual Studio Code.
- **`requirements.txt`**: Lista de dependências Python.
- **`install_and_run.bat`**: Script para facilitar a execução no Windows.
