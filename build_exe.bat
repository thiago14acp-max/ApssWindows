@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Orquestrador de Instalações - Build
echo ========================================
echo.

REM Verificar se o Python está instalado
echo Verificando instalação do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Erro: Python não encontrado. Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

echo Python encontrado.
echo.

REM Instalar dependências
echo Instalando dependências...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Erro ao atualizar pip.
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erro ao instalar dependências do requirements.txt.
    pause
    exit /b 1
)

python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo Erro ao instalar PyInstaller.
    pause
    exit /b 1
)

echo Dependências instaladas com sucesso.
echo.

REM Limpar builds anteriores
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Limpeza concluída.
echo.

REM Compilar executável
echo Compilando executável...
pyinstaller orchestrator.spec --clean
if %errorlevel% neq 0 (
    echo Erro durante a compilação do executável.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build concluído com sucesso!
echo ========================================
echo.
echo Executáveis disponíveis em:
echo   - dist\OrquestradorInstalacoes.exe (Interface Gráfica)
echo   - dist\install_nodejs.exe (Instalador Node.js)
echo   - dist\vscode_installer.exe (Instalador VS Code)
echo.
pause