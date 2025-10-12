# VS Code Installer - Instalador Automático

Script Python que automatiza o download e instalação do Visual Studio Code no Windows 10/11 com todas as opções habilitadas automaticamente.

## Características

- 📥 Download automático da versão mais recente
- 🔧 Instalação silenciosa (sem interação do usuário)
- ✅ Todas as opções habilitadas automaticamente:
  - ✅ Criar ícone na área de trabalho
  - ✅ Adicionar "Abrir com Code" no menu de contexto de arquivos
  - ✅ Adicionar "Abrir com Code" no menu de contexto de pastas
  - ✅ Registrar Code como editor padrão para tipos de arquivo suportados
  - ✅ Adicionar ao PATH (permite usar comando `code`)
- 📊 Barra de progresso durante download
- 🗑️ Limpeza automática de arquivos temporários

## Requisitos

- **Sistema operacional**: Windows 10 ou Windows 11
- **Python**: versão 3.6 ou superior
- **Biblioteca**: `requests` (instalar via pip)
- **Conexão com internet**
- **Aproximadamente 100 MB de espaço livre**

## Instalação

1. Clone ou baixe este repositório:
   ```bash
   git clone https://github.com/username/ferramentas.git
   cd ferramentas
   ```

2. Instale as dependências:
   ```bash
   pip install requests
   ```

## Como Usar

1. Abra o terminal (Prompt de Comando ou PowerShell)
2. Navegue até o diretório do script:
   ```bash
   cd C:\git\Python\ferramentas
   ```
3. Execute o script:
   ```bash
   python vscode_installer.py
   ```
4. Aguarde a conclusão (pode levar alguns minutos)
5. O VS Code estará instalado e pronto para uso!

## O que o Script Faz

1. **Verificação do Sistema**: Confirma que está rodando no Windows
2. **Download**: Baixa o instalador oficial do VS Code (User Installer 64-bit)
   - Mostra barra de progresso em tempo real
   - Salva em diretório temporário
3. **Instalação Silenciosa**: Executa o instalador com flags específicas
   - Todas as opções são marcadas automaticamente
   - Nenhuma interação do usuário é necessária
4. **Limpeza**: Remove arquivos temporários após a instalação

## Opções de Instalação

| Opção | Descrição |
|-------|-----------|
| **Desktop Icon** | Cria atalho na área de trabalho |
| **Context Menu (Files)** | Adiciona opção "Abrir com Code" ao clicar com botão direito em arquivos |
| **Context Menu (Folders)** | Adiciona opção "Abrir com Code" ao clicar com botão direito em pastas |
| **File Associations** | Registra VS Code como editor padrão para arquivos de código |
| **Add to PATH** | Permite usar comando `code` no terminal/PowerShell |

## Troubleshooting

### Erro de conexão
- Verifique sua conexão com internet
- Tente executar o script novamente

### Erro de permissão
- Execute o script como administrador (se necessário)
- Verifique se você tem permissão para instalar programas

### Comando `code` não encontrado
- Reinicie o terminal (Prompt de Comando/PowerShell)
- Faça logout/login se o problema persistir
- Verifique se o PATH foi atualizado corretamente

### Instalação falhou
- Verifique se o VS Code já não está instalado
- Desinstale a versão anterior e tente novamente
- Execute o script como administrador

## Notas Importantes

- O script usa o **User Installer** (não requer privilégios de administrador)
- Instalação é feita no perfil do usuário atual
- Pode ser necessário reiniciar o terminal para usar o comando `code`
- Para desinstalar, use o desinstalador padrão do Windows

## Exemplo de Execução

```
============================================================
    VS Code Installer - Instalador Automático
     Download e instalação do VS Code no Windows
============================================================

📥 Baixando VS Code...
   URL: https://update.code.visualstudio.com/latest/win32-x64-user/stable
   Tamanho estimado: ~100 MB

   Progresso: |████████████████████████████████████████| 100.0% (98.5/98.5 MB)
✅ Download concluído: C:\Users\username\AppData\Local\Temp\VSCodeUserSetup.exe

🔧 Iniciando instalação do VS Code...
   Opções que serão habilitadas:
   ✅ Criar ícone na área de trabalho
   ✅ Adicionar ao menu de contexto (arquivos)
   ✅ Adicionar ao menu de contexto (pastas)
   ✅ Associar com tipos de arquivo suportados
   ✅ Adicionar ao PATH (comando 'code')

   ⏳ Isso pode levar alguns minutos...

✅ VS Code instalado com sucesso!

📋 Notas importantes:
   • O VS Code foi instalado no seu perfil de usuário
   • Reinicie o terminal para usar o comando 'code'
   • Para desinstalar, use o desinstalador padrão do Windows
🗑️  Arquivo temporário removido: C:\Users\username\AppData\Local\Temp\VSCodeUserSetup.exe

🎉 Instalação concluída com sucesso!
   O VS Code está pronto para uso.
```

## Licença e Créditos

- **VS Code**: Desenvolvido pela Microsoft - https://code.visualstudio.com/
- **Script**: Licença MIT
- **Flags de instalação**: Baseadas na documentação do Inno Setup

## Referências

- Download manual: https://code.visualstudio.com/
- Documentação oficial de instalação no Windows
- Referência às flags de instalação silenciosa do Inno Setup
- Issue tracker para problemas e sugestões

---

**Desenvolvido com ❤️ para automatizar sua instalação do VS Code!**