@echo off
REM Script de inicialização da aplicação ws7
REM Compatível com Windows 10 e Windows 11
REM Suporta tanto ws7.py quanto ws7_launcher.exe

setlocal enabledelayedexpansion
chcp 65001 > nul

REM Cores (simuladas com caracteres)
set "CHECK=✓"
set "CROSS=✗"
set "INFO=ℹ"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ws7 - MT5 Monitor                           ║
echo ║                  Iniciando aplicação...                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar se ws7_launcher.exe existe
if exist "ws7_launcher.exe" (
    echo %INFO% Detectado: ws7_launcher.exe
    echo %INFO% Iniciando executável em modo maximizado...
    echo.
    start "" /MAX "ws7_launcher.exe"
    echo %CHECK% Aplicação iniciada!
    echo.
    echo A aplicação deve abrir em seu navegador em alguns segundos.
    echo Se não abrir, acesse: http://localhost:5000
    echo.
    exit /b 0
)

REM Se não encontrou o executável, tenta python ws7.py
echo %INFO% Verificando Python...

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %CROSS% ERRO: Python não foi encontrado!
    echo.
    echo Execute primeiro: verificar_python.bat
    echo.
    pause
    exit /b 1
)

REM Obter versão do Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %CHECK% %PYTHON_VERSION% detectado

REM Verificar se requirements.txt existe
if exist "requirements.txt" (
    echo %INFO% Verificando dependências...
    pip install -q -r requirements.txt
    if %errorlevel% neq 0 (
        echo %CROSS% Erro ao instalar dependências
        echo.
        pause
        exit /b 1
    )
    echo %CHECK% Dependências OK
)

REM Iniciar a aplicação
echo.
echo %INFO% Iniciando ws7.py...
echo.

python ws7.py

if %errorlevel% neq 0 (
    echo.
    echo %CROSS% Erro ao executar a aplicação
    echo.
    echo Se o problema persistir:
    echo 1. Execute: verificar_python.bat
    echo 2. Verifique se todas as dependências estão instaladas
    echo 3. Consulte: SOLUCAO_ERRO_WINDOWS11.md
    echo.
    pause
    exit /b 1
)
