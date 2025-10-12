# Instalador Automático do Node.js para Windows

Este script Python automatiza a instalação e atualização do Node.js no Windows, verificando a versão atual, baixando a versão mais recente e instalando-a de forma silenciosa.

## Requisitos

- Python 3.7 ou superior
- Windows 10 ou superior
- Permissões de administrador
- Conexão com a internet

## Instalação

1. Faça o download dos arquivos do projeto
2. Instale as dependências necessárias executando o comando no prompt de comando ou PowerShell:
   ```
   pip install -r requirements.txt
   ```

## Como Usar

1. Execute o script como administrador:
   - Clique com o botão direito no arquivo `install_nodejs.py`
   - Selecione "Executar como administrador"
   - Ou execute o seguinte comando em um terminal aberto como administrador:
     ```
     python install_nodejs.py
     ```

2. Siga as instruções na tela

### Uso Avançado

#### Execução Automática (sem prompts interativos)
Para automação ou CI/CD, use a flag `-y` ou `--yes`:
```
python install_nodejs.py --yes
```

#### Seleção de Versão e Trilha
- Instalar versão específica:
  ```
  python install_nodejs.py --version 18.19.0
  ```
- Escolher trilha de lançamento:
  ```
  python install_nodejs.py --track current    # Para última versão
  python install_nodejs.py --track lts        # Para LTS (padrão)
  ```

#### Configuração de Proxy Corporativo
Para ambientes corporativos com proxy, você pode:

**1. Usar variáveis de ambiente (recomendado):**
```cmd
set HTTP_PROXY=http://usuario:senha@proxy.empresa.com:8080
set HTTPS_PROXY=http://usuario:senha@proxy.empresa.com:8080
python install_nodejs.py
```

**2. Ou usar a flag --proxy:**
```
python install_nodejs.py --proxy http://usuario:senha@proxy.empresa.com:8080
```

**3. Para autenticação NTLM:**
```cmd
set HTTP_PROXY=http://dominio\usuario:senha@proxy.empresa.com:8080
set HTTPS_PROXY=http://dominio\usuario:senha@proxy.empresa.com:8080
python install_nodejs.py
```

#### Certificados Corporativos (SSL/TLS)

Para ambientes corporativos com certificados personalizados ou firewalls que interceptam SSL/TLS:

**1. Usar certificado CA personalizado (recomendado):**
```cmd
python install_nodejs.py --cacert C:\certificados\empresa-ca.crt
```

**2. Desativar verificação SSL/TLS (não recomendado - apenas para emergências):**
```cmd
python install_nodejs.py --insecure
```

**3. Combinar proxy e certificados:**
```cmd
python install_nodejs.py --proxy http://proxy.empresa.com:8080 --cacert C:\certificados\empresa-ca.crt
```

**⚠️ Aviso importante sobre --insecure:**
- A opção `--insecure` desativa completamente a validação de certificados SSL/TLS
- Isso expõe sua conexão a riscos de segurança significativos
- Use apenas como último recurso em ambientes corporativos restritos
- Prefira sempre usar a opção `--cacert` com um certificado CA válido

#### Timeout de Instalação
Controla o tempo máximo de execução do instalador MSI. O padrão é 300 segundos (5 minutos). Em máquinas lentas ou ambientes corporativos com antivírus/policies restritivas, pode ser necessário aumentar este valor.

**Exemplo de uso:**
```bash
python install_nodejs.py --install-timeout 900
```

No exemplo acima, o timeout é aumentado para 900 segundos (15 minutos), ideal para ambientes corporativos ou máquinas com desempenho limitado.

#### Instalação para Todos os Usuários
Para instalar o Node.js para todos os usuários do sistema (requer administrador):
```bash
python install_nodejs.py --all-users
```

#### Timeout de Download
Controla o tempo máximo para operações de rede (download, verificação de disponibilidade). O padrão é 300 segundos (5 minutos). Útil para conexões lentas:
```bash
python install_nodejs.py --download-timeout 600
```

#### Controle de Fallback de Arquitetura
Para sistemas ARM64 onde o instalador nativo não está disponível, controle o comportamento de fallback para x64:
```bash
# Permitir fallback automático de ARM64 para x64 sem confirmação
python install_nodejs.py --allow-arch-fallback

# Combinar com modo automático para CI/CD
python install_nodejs.py --yes --allow-arch-fallback
```

#### Logs Detalhados
Para aumentar a verbosidade dos logs e opcionalmente salvar em um arquivo:
```bash
# Modo verbose (mais detalhes no console)
python install_nodejs.py --verbose

# Salvar logs em arquivo
python install_nodejs.py --log-file nodejs-install.log

# Combinar verbose e arquivo de log
python install_nodejs.py --verbose --log-file nodejs-install.log
```

#### Instalação automática do Gemini CLI
- Após instalar/atualizar o Node.js, o script tenta instalar globalmente `@google/gemini-cli`.
- O PATH é ajustado temporariamente apenas para a execução do npm dentro do script; reabra o terminal para usar o comando `gemini`.
- Para verificar a instalação:
  - `gemini --help`
  - `npm list -g @google/gemini-cli`
- Se necessário, você pode instalar manualmente:
  - `npm install -g @google/gemini-cli`

#### Timeout do npm (instalação de pacotes globais)
O tempo limite padrão para a instalação de pacotes npm é 300 segundos. Ajuste conforme necessário:

```bash
python install_nodejs.py --npm-timeout 600
```

#### Instalação automática do Qwen Code CLI
- Após instalar/atualizar o Node.js e o Gemini CLI, o script tenta instalar globalmente `@qwen-code/qwen-code@latest`.
- O PATH é ajustado temporariamente apenas para a execução do npm dentro do script; reabra o terminal para usar o comando `qwen`.
- Para verificar a instalação:
  - `qwen --version`
  - `npm list -g @qwen-code/qwen-code`
- Se necessário, você pode instalar manualmente:
  - `npm install -g @qwen-code/qwen-code@latest`

## Funcionalidades

- **Verificação automática**: Detecta se o Node.js já está instalado no sistema (inclui instalações por usuário)
- **Comparação de versões**: Compara a versão instalada com a versão mais recente disponível
- **Download inteligente**: Baixa automaticamente o instalador correto para sua arquitetura (x64, x86, ARM64 com fallback)
- **Instalação silenciosa**: Realiza a instalação sem necessidade de interação do usuário
- **Instalação flexível**: Opção de instalar para todos os usuários ou apenas para o usuário atual
- **Timeouts configuráveis**: Controla tempos limite para instalação e downloads
- **Sistema de logs**: Opção de logs detalhados e persistência em arquivo para suporte
- **Interface amigável**: Exibe mensagens claras em português sobre cada etapa do processo
- **Validação**: Verificação de integridade SHA256 dos arquivos baixados
- **Confirmações inteligentes**: Solicita confirmação para operações de risco (ex: fallback ARM64→x64)
- **Controle de fallback**: Opção de permitir fallback automático de arquitetura sem confirmação
- **Política do PowerShell automática**: Ajusta `Set-ExecutionPolicy RemoteSigned` (escopo `CurrentUser`) com tratamento de erro não bloqueante.
- **Instalação do Gemini CLI**: Após concluir o Node.js, instala globalmente `@google/gemini-cli` via npm, com PATH temporário atualizado, timeout configurável e logs.
- **Instalação do Qwen Code CLI**: Após concluir o Node.js e Gemini CLI, instala globalmente `@qwen-code/qwen-code@latest` via npm, com PATH temporário atualizado, timeout configurável e logs.

## Exemplos de Saída

### Caso 1: Node.js não está instalado
```
============================================================
Instalador Automático do Node.js para Windows
============================================================

Verificando instalação existente do Node.js...
Node.js não está instalado.
Verificando a versão mais recente do Node.js...
Versão mais recente disponível: 20.10.0 (LTS)
Iniciando instalação...
Detectada arquitetura: x64
Baixando node-v20.10.0-x64.msi...
[==================================================] 100%
Download concluído: C:\Users\Usuario\AppData\Local\Temp\tmp12345.msi
Iniciando instalação do Node.js...
Isso pode levar alguns minutos...
Instalação concluída com sucesso!

============================================================
Processo concluído com sucesso!
Node.js versão 20.10.0 foi instalado com sucesso!
Você pode precisar reiniciar o terminal para usar o novo Node.js.

Instalando pacote @google/gemini-cli...
✓ Pacote @google/gemini-cli instalado com sucesso!

Instalando pacote @qwen-code/qwen-code...
✓ Pacote @qwen-code/qwen-code instalado com sucesso!
============================================================
```

### Caso 2: Node.js já está atualizado
```
============================================================
Instalador Automático do Node.js para Windows
============================================================

Verificando instalação existente do Node.js...
Node.js versão 20.10.0 está instalado.
Verificando a versão mais recente do Node.js...
Versão mais recente disponível: 20.10.0 (LTS)
Seu Node.js (v20.10.0) já está atualizado!
```

## Solução de Problemas

### Erro de permissões
Se o script exibir uma mensagem sobre falta de permissões:
1. Clique com o botão direito no script
2. Selecione "Executar como administrador"
3. Confirme na janela do Controle de Conta de Usuário

### Erro de rede
Se ocorrer um erro ao obter a versão mais recente ou ao baixar o instalador:
1. Verifique sua conexão com a internet
2. Tente executar o script novamente
3. Verifique se seu firewall ou antivírus não está bloqueando o script

### Erro ao instalar a biblioteca requests
Se receber uma mensagem sobre a biblioteca requests não estar instalada:
1. Execute o comando: `pip install requests`
2. Ou instale as dependências com: `pip install -r requirements.txt`

### Timeout de instalação
Se a instalação exceder 5 minutos ou ocorrer um erro de timeout:
1. Use a flag `--install-timeout` para aumentar o tempo limite
2. Exemplo: `python install_nodejs.py --install-timeout 900` (15 minutos)
3. Isso é comum em máquinas lentas ou ambientes corporativos com antivírus pesado

### Falha ao configurar a política de execução do PowerShell
**Sintomas:** mensagens como "Falha ao configurar política de execução", "Access is denied" ou aviso de política definida via diretiva de grupo (GPO).

**Causas possíveis:** restrições corporativas (GPO), execução em ambiente bloqueado ou uso de shell diferente (Windows PowerShell vs PowerShell 7).

**O que o script faz:** segue a execução mesmo se a configuração falhar, exibindo aviso.

**Soluções:**
1. Execute manualmente em uma janela do PowerShell (como usuário atual):
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   ```
2. Verifique o estado atual:
   ```powershell
   Get-ExecutionPolicy -List
   ```
3. Em ambientes com GPO, solicite à TI a liberação ou execute os passos conforme a política da empresa.
4. Caso tenha múltiplos shells, teste com `powershell.exe` e `pwsh` (PowerShell 7).

### Falha ao instalar pacotes npm globais (@google/gemini-cli ou @qwen-code/qwen-code)
**npm não encontrado / "npm não é reconhecido":**
- Feche e reabra o terminal após a instalação do Node.js.
- Verifique se estes caminhos estão no PATH do usuário:
  - `C:\Program Files\nodejs`
  - `%APPDATA%\npm`
- Confirme com:
  ```cmd
  where npm
  ```

**Proxy/Firewall corporativo:**
- Configure variáveis de ambiente antes de executar o script:
  ```cmd
  set HTTP_PROXY=http://usuario:senha@proxy.empresa.com:8080
  set HTTPS_PROXY=http://usuario:senha@proxy.empresa.com:8080
  ```
- E/ou configure o npm:
  ```cmd
  npm config set proxy http://usuario:senha@proxy.empresa.com:8080
  npm config set https-proxy http://usuario:senha@proxy.empresa.com:8080
  ```

**Certificados corporativos (SSL/TLS):**
- Prefira apontar o certificado da CA corporativa para o npm:
  ```cmd
  npm config set cafile C:\certificados\empresa-ca.crt
  ```
- Evite desabilitar validação; se for emergência, restaure depois:
  ```cmd
  npm config set strict-ssl false
  ```

**Permissões/Prefix (erros EPERM/EACCES):**
- Ajuste o prefixo para o diretório do usuário e reabra o terminal:
  ```cmd
  npm config set prefix "%APPDATA%\npm"
  ```
- Alternativamente, execute o terminal como Administrador.

**Timeout:**
- Aumente o tempo limite do npm conforme a rede/antivírus:
  ```bash
  python install_nodejs.py --npm-timeout 900
  ```

**Conflito com nvm-windows:**
- Se usa nvm-windows, selecione a versão ativa e instale os CLIs nela:
  ```cmd
  nvm use latest
  npm install -g @google/gemini-cli
  npm install -g @qwen-code/qwen-code@latest
  ```

## Notas Técnicas

- O script baixa e instala automaticamente a versão LTS (Long Term Support) mais recente do Node.js
- A arquitetura do sistema (x64 ou x86) é detectada automaticamente
- A instalação é realizada silenciosamente, sem necessidade de interação do usuário
- O instalador temporário é removido após a conclusão do processo
- O script requer conexão com internet para baixar o instalador mais recente

## Nota de Segurança: Política de Execução do PowerShell
O script ajusta a política de execução do PowerShell para `RemoteSigned` no escopo `CurrentUser`.

- O que muda: scripts locais podem ser executados sem assinatura; scripts baixados exigem assinatura de um publicador confiável.
- Escopo: a alteração vale apenas para o usuário atual, não para todo o sistema.
- Como verificar o estado atual:
  ```powershell
  Get-ExecutionPolicy -List
  ```
- Como reverter para o padrão restrito do usuário atual:
  ```powershell
  Set-ExecutionPolicy Restricted -Scope CurrentUser
  ```
- Alternativa (padrão do sistema):
  ```powershell
  Set-ExecutionPolicy Default -Scope CurrentUser
  ```

## Uso em CI

O script retorna códigos de saída padronizados que podem ser usados em pipelines de CI/CD:

- **0**: Sucesso - Node.js instalado/atualizado com êxito
- **1**: Erro - Falha na instalação, download, ou erro de validação
- **2**: Cancelamento pelo usuário - Operação cancelada interativamente
- **130**: Interrupção por Ctrl+C - Processo interrompido pelo usuário

### Exemplo de uso em CI
```bash
python install_nodejs.py --yes
if [ $? -eq 0 ]; then
  echo "Node.js instalado com sucesso!"
else
  echo "Falha na instalação (código: $?)"
  exit $?
fi
```

## Licença

Este software é fornecido "como está", sem garantias de qualquer tipo.