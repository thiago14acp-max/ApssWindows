@echo off
REM Script para instalar dependências e executar o Orquestrador de Instalações

echo Iniciando instalacao das dependencias...

REM Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Erro: Python nao encontrado. Por favor, instale o Python antes de executar este script.
    pause
    exit /b 1
)

REM Verifica se o pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo Erro: Pip nao encontrado. Por favor, instale o pip antes de executar este script.
    pause
    exit /b 1
)

echo Instalando dependencias do arquivo requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo Erro durante a instalacao das dependencias.
    pause
    exit /b 1
)

echo Dependencias instaladas com sucesso!

echo Executando o Orquestrador de Instalações...
python orchestrator_gui.py

if errorlevel 1 (
    echo Erro durante a execucao do script orchestrator_gui.py
    pause
    exit /b 1
)

echo Execucao concluida.
pause