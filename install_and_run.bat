@echo off
setlocal enableextensions enabledelayedexpansion
pushd "%~dp0"

REM Script para instalar dependências e executar a aplicação

echo Verificando a instalação do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não está instalado ou não está no PATH.
    echo Por favor, instale o Python 3.7+ e tente novamente.
    pause
    popd
    endlocal
    exit /b 1
)

echo Instalando dependências do requirements.txt...
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo Falha ao instalar as dependências.
    pause
    popd
    endlocal
    exit /b 1
)

echo Iniciando a aplicação...
python "%~dp0src\main.py"

popd
endlocal
pause