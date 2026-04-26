@echo off
REM Script de inicialização da aplicação ws7
REM Compatível com Windows 10 e Windows 11
REM Detecta automaticamente: executavel compilado, launcher.py ou ws7.py

setlocal enabledelayedexpansion
chcp 65001 > nul

REM Cores (simuladas com caracteres)
set "CHECK=✓"
set "CROSS=✗"
set "INFO=ℹ"
set "WARN=⚠"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                   ws7 - MT5 Monitor                           ║
echo ║                  Iniciando aplicação...                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM ==========================================
REM  1. TENTAR EXECUTAVEL COMPILADO
REM ==========================================
if exist "dist\VolatForex_Monitor_Pro.exe" (
    echo %CHECK% Detectado: VolatForex_Monitor_Pro.exe (dist\)
    echo %INFO% Iniciando executavel compilado...
    echo.
    start "" /MAX "dist\VolatForex_Monitor_Pro.exe"
    echo %CHECK% Aplicação iniciada!
    echo.
    echo A aplicação deve abrir em alguns segundos.
    echo Se não abrir, acesse: http://localhost:5000
    echo.
    exit /b 0
)

if exist "VolatForex_Monitor_Pro.exe" (
    echo %CHECK% Detectado: VolatForex_Monitor_Pro.exe
    echo %INFO% Iniciando executavel compilado...
    echo.
    start "" /MAX "VolatForex_Monitor_Pro.exe"
    echo %CHECK% Aplicação iniciada!
    echo.
    echo A aplicação deve abrir em alguns segundos.
    echo Se não abrir, acesse: http://localhost:5000
    echo.
    exit /b 0
)

REM ==========================================
REM  2. TENTAR ws7_launcher.exe
REM ==========================================
if exist "ws7_launcher.exe" (
    echo %CHECK% Detectado: ws7_launcher.exe
    echo %INFO% Iniciando executavel em modo maximizado...
    echo.
    start "" /MAX "ws7_launcher.exe"
    echo %CHECK% Aplicação iniciada!
    echo.
    echo A aplicação deve abrir em alguns segundos.
    echo Se não abrir, acesse: http://localhost:5000
    echo.
    exit /b 0
)

REM ==========================================
REM  3. TENTAR ws7_launcher.py (modo standalone)
REM ==========================================
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
if not exist "requirements.txt" (
    echo %CROSS% ERRO: requirements.txt nao encontrado!
    echo.
    echo Baixe novamente o pacote completo da aplicacao.
    echo.
    pause
    exit /b 1
)

echo %INFO% Verificando dependencias...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo %CROSS% Erro ao instalar dependencias
    echo.
    pause
    exit /b 1
)
echo %CHECK% Dependencias OK

REM ==========================================
REM  3a. TENTAR ws7_launcher.py (janela nativa)
REM ==========================================
if exist "ws7_launcher.py" (
    echo.
    echo %INFO% Iniciando ws7_launcher.py (janela nativa)...
    echo.
    python ws7_launcher.py
    if %errorlevel% equ 0 exit /b 0
    echo %WARN% Falha ao iniciar ws7_launcher.py, tentando modo navegador...
    echo.
)

REM ==========================================
REM  3b. TENTAR ws7.py (modo navegador)
REM ==========================================
echo %INFO% Iniciando ws7.py (modo navegador)...
echo.
echo A aplicacao abrira no navegador: http://localhost:5000
echo.

python ws7.py

if %errorlevel% neq 0 (
    echo.
    echo %CROSS% Erro ao executar a aplicacao
    echo.
    echo Diagnosticos:
    echo 1. Execute: verificar_python.bat
    echo 2. Consulte: SOLUCAO_ERRO_WINDOWS11.md
    echo 3. Execute o diagnostico: diagnosticar_windows11.bat
    echo.
    pause
    exit /b 1
)
