@echo off
REM Script para verificar e corrigir problemas com Python no Windows 11
REM Compatível com Windows 10 e Windows 11
REM Inclui instalação automática de requisitos

setlocal enabledelayedexpansion
chcp 65001 > nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         Verificador de Python - ws7 Launcher                  ║
echo ║                                                                ║
echo ║  Este script verifica se Python 3.12 está instalado e         ║
echo ║  configurado corretamente no seu sistema.                     ║
echo ║                                                                ║
echo ║  Também instala automaticamente todos os requisitos           ║
echo ║  necessários para executar a aplicação.                       ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar se Python está instalado
echo [1/4] Verificando se Python 3.12 está instalado...
python --version >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Python não foi encontrado no PATH!
    echo.
    echo Soluções:
    echo.
    echo 1. Instale Python 3.12 de: https://www.python.org/downloads/
    echo    IMPORTANTE: Marque "Add Python to PATH" durante a instalação
    echo.
    echo 2. Após instalar, reinicie este script
    echo.
    echo 3. Se já instalou, reinicie o computador
    echo.
    pause
    exit /b 1
)

REM Obter versão do Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% encontrado

REM Verificar se é Python 3.12
echo %PYTHON_VERSION% | findstr /R "3.12" >nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  AVISO: Versão do Python pode não ser 3.12
    echo    Versão encontrada: %PYTHON_VERSION%
    echo.
    echo    A aplicação foi desenvolvida para Python 3.12
    echo    Outras versões podem ter compatibilidade limitada
    echo.
)

REM Verificar se pip está instalado
echo.
echo [2/4] Verificando se pip está instalado...
pip --version >nul 2>&1

if %errorlevel% neq 0 (
    echo ❌ ERRO: pip não foi encontrado!
    echo.
    echo Reinstale Python e marque "pip" durante a instalação
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('pip --version 2^>^&1') do set PIP_VERSION=%%i
echo ✅ %PIP_VERSION% encontrado

REM Atualizar pip para versão mais recente
echo.
echo [3/4] Atualizando pip para versão mais recente...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ pip atualizado

REM Instalar/verificar dependências
echo.
echo [4/4] Instalando/verificando dependências da aplicação...
echo.

REM Verificar se requirements.txt existe
if not exist "requirements.txt" (
    echo.
    echo ❌ ERRO: requirements.txt não encontrado!
    echo.
    echo Certifique-se de que todos os arquivos do projeto foram extraídos.
    echo Baixe novamente o pacote completo.
    echo.
    pause
    exit /b 1
)

REM Instalar dependências
echo Instalando dependências (isso pode levar alguns minutos)...
echo.
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Falha ao instalar dependências
    echo.
    echo Tente novamente com:
    echo pip install --upgrade -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Todas as dependências estão instaladas com sucesso!

REM Sucesso
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ TUDO OK!                                ║
echo ║                                                                ║
echo ║  Seu sistema está pronto para executar a aplicação ws7        ║
echo ║                                                                ║
echo ║  Para iniciar a aplicação, execute:                           ║
echo ║  - ws7_launcher.exe (se disponível)                           ║
echo ║  - ou python ws7.py                                           ║
echo ║  - ou clique em iniciar.bat                                   ║
echo ║                                                                ║
echo ║  Requisitos instalados:                                       ║
echo ║  - Flask 2.3.3                                                ║
echo ║  - Waitress 2.1.2                                             ║
echo ║  - Requests 2.31.0                                            ║
echo ║  - PyWebview 4.4.1                                            ║
echo ║  - Python-dotenv 1.0.0                                        ║
echo ║  - E todas as dependências necessárias                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

pause
