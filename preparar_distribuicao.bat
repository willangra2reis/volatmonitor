@echo off
REM Prepara pasta de distribuicao completa
REM Inclui executavel compilado + scripts fallback (opcional)

setlocal enabledelayedexpansion
chcp 65001 > nul

echo.
echo ==========================================
echo  Preparando Distribuicao - ws7
echo ==========================================
echo.

set SOURCE=output\ws7_launcher.dist
set DEST=VolatForex_Monitor_Pro

if not exist "%SOURCE%\ws7_launcher.exe" (
    echo [ERRO] Executavel nao encontrado em %SOURCE%
    echo Execute primeiro: build_nuitka.bat
    pause
    exit /b 1
)

REM Criar pasta de distribuicao
echo [INFO] Criando pasta %DEST%...
if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%"

REM Copiar executavel compilado (COM Python embutido)
echo [INFO] Copiando executavel compilado...
xcopy /e /i /y "%SOURCE%\*" "%DEST%\"

REM Renomear executavel para nome amigavel
copy "%DEST%\ws7_launcher.exe" "%DEST%\VolatForex_Monitor_Pro.exe" >nul

REM Criar LEIA-ME.txt
echo [INFO] Criando instrucoes...
(
    echo ==========================================
    echo   VolatForex Monitor Pro
echo ==========================================
    echo.
    echo  INSTALACAO NAO NECESSARIA
echo  ===========================
    echo  Este programa ja contem Python embutido.
    echo  NAO e necessario instalar Python.
    echo.
    echo  COMO USAR
echo  ==========
    echo  1. Execute: VolatForex_Monitor_Pro.exe
    echo  2. Aguarde a janela abrir (pode levar alguns segundos)
    echo  3. Faca login com seu email
    echo.
    echo  REQUISITOS MINIMOS
echo  ===================
    echo  - Windows 10 ou 11 (64 bits)
    echo  - Conexao com internet (para autenticacao)
    echo  - MetaTrader 5 rodando com o EA ativo
    echo.
    echo  SOLUCAO DE PROBLEMAS
echo  =====================
    echo  Se o programa nao abrir:
    echo  1. Verifique se esta pasta foi extraida COMPLETA
    echo     (nao execute de dentro do ZIP)
    echo  2. Se Windows bloquear, clique em "Mais info" 
    echo     e depois "Executar assim mesmo"
    echo  3. Antivirus: adicione uma excecao para esta pasta
    echo.
    echo  Se precisar rodar via Python (modo tecnico):
    echo  1. Instale Python 3.12: https://python.org/downloads/
    echo  2. Execute: verificar_python.bat
    echo  3. Execute: iniciar.bat
    echo.
    echo  Suporte: [seu-email-aqui]
    echo ==========================================
) > "%DEST%\LEIA-ME.txt"

REM Opcional: incluir scripts fallback para usuarios avancados
echo.
echo [INFO] Incluir scripts de fallback (Python)?
echo        (para usuarios que querem rodar via codigo fonte)
echo.
choice /c SN /m "Incluir scripts .bat"
if %errorlevel% equ 1 (
    echo [INFO] Copiando scripts fallback...
    copy "iniciar.bat" "%DEST%\iniciar.bat" >nul
    copy "verificar_python.bat" "%DEST%\verificar_python.bat" >nul
    copy "diagnosticar_windows11.bat" "%DEST%\diagnosticar_windows11.bat" >nul
    copy "requirements.txt" "%DEST%\requirements.txt" >nul
    copy "ws7.py" "%DEST%\ws7.py" >nul
    copy "ws7_launcher.py" "%DEST%\ws7_launcher.py" >nul
    copy ".env.dist" "%DEST%\.env" >nul
    echo [OK] Scripts fallback incluidos
) else (
    echo [INFO] Apenas executavel standalone (mais limpo)
)

echo.
echo ==========================================
echo  Distribuicao pronta!
echo ==========================================
echo.
echo Pasta: %DEST%\
echo.
echo Opcoes de distribuicao:
echo 1. Compacte %DEST% em ZIP e envie
echo 2. Use Inno Setup para criar instalador .exe
echo.
pause
