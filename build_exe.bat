@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Orquestrador de InstalaÃ§Ãµes - Build
echo ========================================
echo.

REM Verificar se o Python estÃ¡ instalado
echo Verificando instalaÃ§Ã£o do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python nÃ£o encontrado. Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

echo Python encontrado.
echo.

REM Instalar dependÃªncias
echo Instalando dependÃªncias...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Erro ao atualizar pip.
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erro ao instalar dependÃªncias do requirements.txt.
    pause
    exit /b 1
)

python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo Erro ao instalar PyInstaller.
    pause
    exit /b 1
)

echo DependÃªncias instaladas com sucesso.
echo.

REM Limpar builds anteriores
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Limpeza concluÃ­da.
echo.

REM Compilar executÃ¡vel
echo Compilando executÃ¡vel...
pyinstaller orchestrator.spec --clean
if %errorlevel% neq 0 (
    echo Erro durante a compilaÃ§Ã£o do executÃ¡vel.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build concluÃ­do com sucesso!
echo ========================================
echo.
echo ExecutÃ¡veis disponÃ­veis em:
echo   - dist\OrquestradorInstalacoes.exe (Interface GrÃ¡fica)
echo   - dist\install_nodejs.exe (Instalador Node.js)
echo   - dist\vscode_installer.exe (Instalador VS Code)
echo   - dist\git_installer.exe (Instalador Git)
echo   - dist\mcp_excel_installer.exe (Instalador MCP Excel Server)
echo.
pause
