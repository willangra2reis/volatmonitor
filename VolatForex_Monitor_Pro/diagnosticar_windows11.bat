@echo off
REM Diagnostico Completo ws7 - Windows 11
setlocal enabledelayedexpansion
chcp 65001 > nul

set ERRORS=0
set WARNINGS=0

cls
echo.
echo ================================================================
echo              DIAGNOSTICO ws7 - Windows 11
echo ================================================================
echo.

REM 1. SISTEMA
echo [INFO] Sistema: %OS%

REM 2. PYTHON
echo.
echo [INFO] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERRO] Python NAO encontrado no PATH
    echo   Instale Python 3.12 e marque "Add to PATH"
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo   [OK] %%i
)

REM 3. PIP
echo.
echo [INFO] Verificando pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERRO] pip NAO encontrado
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('pip --version 2^>^&1') do echo   [OK] %%i
)

REM 4. ARQUIVOS DO PROJETO
echo.
echo [INFO] Verificando arquivos do projeto...
if not exist "ws7.py" (echo   [ERRO] ws7.py ausente & set /a ERRORS+=1) else (echo   [OK] ws7.py)
if not exist "requirements.txt" (echo   [ERRO] requirements.txt ausente & set /a ERRORS+=1) else (echo   [OK] requirements.txt)
if not exist ".env" (
    echo   [ERRO] .env ausente (REQUERIDO)
    echo   Crie: FLASK_SECRET_KEY=sua_chave_secreta_aqui
    set /a ERRORS+=1
) else (echo   [OK] .env)
if exist ".env.example" (echo   [OK] .env.example (template))

REM 5. DEPENDENCIAS PYTHON
echo.
echo [INFO] Verificando dependencias Python...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] Flask nao instalado & set /a ERRORS+=1) else (echo   [OK] Flask)
python -c "import waitress" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] Waitress nao instalado & set /a ERRORS+=1) else (echo   [OK] Waitress)
python -c "import requests" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] Requests nao instalado & set /a ERRORS+=1) else (echo   [OK] Requests)
python -c "import flask_cors" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] Flask-CORS nao instalado & set /a ERRORS+=1) else (echo   [OK] Flask-CORS)
python -c "import dotenv" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] python-dotenv nao instalado & set /a ERRORS+=1) else (echo   [OK] python-dotenv)
python -c "import webview" 2>nul
if %errorlevel% neq 0 (echo   [AVISO] PyWebview nao instalado (necessario para janela nativa) & set /a WARNINGS+=1) else (echo   [OK] PyWebview)

REM 6. MODULOS LOCAIS
echo.
echo [INFO] Verificando modulos locais...
python -c "import auth_middleware" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] auth_middleware.py & set /a ERRORS+=1) else (echo   [OK] auth_middleware.py)
python -c "import google_auth" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] google_auth.py & set /a ERRORS+=1) else (echo   [OK] google_auth.py)
python -c "import credentials_manager" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] credentials_manager.py & set /a ERRORS+=1) else (echo   [OK] credentials_manager.py)
python -c "import symbol_mapper" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] symbol_mapper.py & set /a ERRORS+=1) else (echo   [OK] symbol_mapper.py)
python -c "import technical_indicators" 2>nul
if %errorlevel% neq 0 (echo   [ERRO] technical_indicators.py & set /a ERRORS+=1) else (echo   [OK] technical_indicators.py)

REM 7. EXECUTAVEIS
echo.
echo [INFO] Verificando executaveis...
if exist "dist\VolatForex_Monitor_Pro.exe" (echo   [OK] dist\VolatForex_Monitor_Pro.exe)
if exist "VolatForex_Monitor_Pro.exe" (echo   [OK] VolatForex_Monitor_Pro.exe)
if not exist "dist\VolatForex_Monitor_Pro.exe" if not exist "VolatForex_Monitor_Pro.exe" (echo   [INFO] Nenhum executavel compilado)

REM 8. PORTA 5000
echo.
echo [INFO] Verificando porta 5000...
netstat -ano | findstr ":5000" >nul
if %errorlevel% equ 0 (echo   [AVISO] Porta 5000 em uso & set /a WARNINGS+=1) else (echo   [OK] Porta 5000 livre)

REM 9. RESUMO
echo.
echo ================================================================
echo                        RESULTADO
echo ================================================================
echo.
if %ERRORS% gtr 0 (
    echo   [ERRO] %ERRORS% erro(s) encontrado(s)
    echo   A aplicacao NAO vai funcionar.
    echo   Execute: verificar_python.bat
    echo   Ou: pip install -r requirements.txt
)
if %WARNINGS% gtr 0 (
    echo   [AVISO] %WARNINGS% aviso(s)
    echo   A aplicacao pode funcionar com limitacoes.
)
if %ERRORS% equ 0 if %WARNINGS% equ 0 (
    echo   [OK] Tudo certo! Execute: iniciar.bat
)
echo.
pause
