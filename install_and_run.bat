@echo off
REM Script para instalar dependências e executar a aplicação

echo Verificando a instalação do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não está instalado ou não está no PATH.
    echo Por favor, instale o Python 3.7+ e tente novamente.
    pause
    exit /b 1
)

echo Instalando dependências do requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Falha ao instalar as dependências.
    pause
    exit /b 1
)

echo Iniciando a aplicação...
python src/main.py

pause
