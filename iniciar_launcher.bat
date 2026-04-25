@echo off
REM Script para iniciar ws7_launcher.exe com verificações
REM Compatível com Windows 10 e Windows 11

setlocal enabledelayedexpansion
chcp 65001 > nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ws7 - MT5 Monitor                           ║
echo ║              Iniciando aplicação (Launcher)...                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar se o executável existe
if not exist "ws7_launcher.exe" (
    echo ❌ ERRO: ws7_launcher.exe não foi encontrado!
    echo.
    echo Certifique-se de que o arquivo ws7_launcher.exe está na mesma
    echo pasta deste script.
    echo.
    pause
    exit /b 1
)

echo ✅ ws7_launcher.exe encontrado

REM Verificar se Python está instalado
echo.
echo Verificando se Python 3.12 está instalado...
python --version >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Python não foi encontrado!
    echo.
    echo Execute primeiro: verificar_python.bat
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% detectado

REM Verificar se requirements.txt existe
if exist "requirements.txt" (
    echo.
    echo Verificando dependências...
    pip install -q -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar dependências
        echo.
        echo Execute: verificar_python.bat
        echo.
        pause
        exit /b 1
    )
    echo ✅ Dependências OK
)

REM Iniciar a aplicação
echo.
echo ℹ️  Iniciando ws7_launcher.exe...
echo.

REM Iniciar maximizado: /MAX
start "" /MAX "ws7_launcher.exe"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erro ao executar ws7_launcher.exe
    echo.
    echo Se o problema persistir:
    echo 1. Execute: verificar_python.bat
    echo 2. Verifique se todas as dependências estão instaladas
    echo 3. Tente executar: python ws7.py
    echo.
    pause
    exit /b 1
)

echo ✅ Aplicação iniciada com sucesso!
echo.
echo A aplicação deve abrir em seu navegador em alguns segundos.
echo Se não abrir, acesse: http://localhost:5000
echo.
