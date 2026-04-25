@echo off
REM ==========================================
REM Build Script - VolatForex Monitor Pro
REM Compila aplicação com Nuitka + WebView2
REM ==========================================

echo.
echo ========================================
echo  VolatForex Monitor Pro - Build Script
echo ========================================
echo.

REM --- Verificar se Python está instalado ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM --- Verificar se Nuitka está instalado ---
python -c "import nuitka" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Nuitka nao encontrado!
    echo [INFO] Instalando dependencias de build...
    pip install -r requirements_build.txt
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias
        pause
        exit /b 1
    )
)

echo [OK] Nuitka instalado
echo.

REM --- Limpar builds anteriores ---
echo [INFO] Limpando builds anteriores...
if exist "output" rmdir /s /q "output"
if exist "ws7_launcher.build" rmdir /s /q "ws7_launcher.build"
if exist "ws7_launcher.dist" rmdir /s /q "ws7_launcher.dist"
if exist "ws7_launcher.onefile-build" rmdir /s /q "ws7_launcher.onefile-build"
echo [OK] Limpeza concluida
echo.

REM --- Verificar se ícone existe ---
if not exist "VOLAT-removebg.ico" (
    echo [AVISO] Icone VOLAT-removebg.ico nao encontrado
    echo [INFO] Executavel sera criado sem icone
    set ICON_PARAM=
) else (
    echo [OK] Icone encontrado
    set ICON_PARAM=--windows-icon-from-ico=VOLAT-removebg.ico
)

echo.
echo ========================================
echo  Iniciando Compilacao com Nuitka
echo ========================================
echo.
echo [INFO] Modo: STANDALONE (pasta com multiplos arquivos)
echo [INFO] Tempo estimado: 10-20 minutos (primeira vez)
echo [INFO] Aguarde... Nao feche esta janela!
echo.

REM --- Compilar com Nuitka ---
python -m nuitka ^
    --standalone ^
    --enable-plugin=anti-bloat ^
    --windows-disable-console ^
    %ICON_PARAM% ^
    --include-package=flask ^
    --include-package=flask_cors ^
    --include-package=waitress ^
    --include-package=webview.platforms.winforms ^
    --include-package=requests ^
    --include-data-dir=templates=templates ^
    --include-data-dir=static=static ^
    --include-data-file=symbol_mapping.json=symbol_mapping.json ^
    --include-data-file=.env=.env ^
    --output-dir=output ^
    --company-name="VolatForex" ^
    --product-name="VolatForex Monitor Pro" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0 ^
    --file-description="MT5 Trading Monitor - Standalone Edition" ^
    --assume-yes-for-downloads ^
    ws7_launcher.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha na compilacao!
    echo [INFO] Verifique os erros acima
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Compilacao Concluida com Sucesso!
echo ========================================
echo.

REM --- Verificar se executável foi criado ---
if exist "output\ws7_launcher.dist\ws7_launcher.exe" (
    echo [OK] Executavel criado: output\ws7_launcher.dist\ws7_launcher.exe
    echo.
    echo [INFO] Estrutura de arquivos:
    dir /b "output\ws7_launcher.dist"
    echo.
    echo ========================================
    echo  Proximos Passos:
    echo ========================================
    echo.
    echo 1. Teste o executavel:
    echo    output\ws7_launcher.dist\ws7_launcher.exe
    echo.
    echo 2. Distribua a pasta completa:
    echo    output\ws7_launcher.dist\
    echo.
    echo 3. (Opcional) Renomeie a pasta para:
    echo    VolatForexMonitorPro\
    echo.
    echo 4. (Opcional) Crie instalador com Inno Setup
    echo.
    echo ========================================
) else (
    echo [ERRO] Executavel nao encontrado!
    echo [INFO] Verifique os logs acima
)

echo.
pause
