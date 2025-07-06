@echo off
REM Script SIMPLIFICADO para arranque automático
REM Enfoque directo y robusto

set LOG_FILE=C:\Users\yessi\bar-code-scaner\startup.log
set PROJECT_DIR=C:\Users\yessi\bar-code-scaner

echo ================================== > %LOG_FILE%
echo SCANNER SERVER - ARRANQUE AUTOMATICO >> %LOG_FILE%
echo %date% %time% >> %LOG_FILE%
echo ================================== >> %LOG_FILE%

echo 🚀 INICIANDO SCANNER SERVER
echo ===========================

cd /d "%PROJECT_DIR%"

REM Verificaciones básicas
if not exist "server_https.py" goto error_file
if not exist ".venv\Scripts\python.exe" goto error_venv

echo ✅ Archivos verificados

REM Limpiar procesos anteriores
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 >nul

echo ⏳ Iniciando servidor...
echo [%time%] Iniciando servidor >> %LOG_FILE%

REM Ejecutar servidor minimizado
start "Scanner Server" /MIN .venv\Scripts\python.exe server_https.py

REM Esperar arranque
timeout /t 12 >nul

REM Verificar funcionamiento
curl -k https://localhost:5443/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SERVIDOR FUNCIONANDO >> %LOG_FILE%
    echo ✅ SERVIDOR FUNCIONANDO
    echo 🌐 https://localhost:5443/
    start https://localhost:5443/
    goto end
) else (
    echo ❌ SERVIDOR NO RESPONDE >> %LOG_FILE%
    echo ❌ SERVIDOR NO RESPONDE
)

goto end

:error_file
echo ❌ ERROR: server_https.py no encontrado >> %LOG_FILE%
echo ❌ ERROR: server_https.py no encontrado
goto end

:error_venv
echo ❌ ERROR: Entorno virtual no encontrado >> %LOG_FILE%
echo ❌ ERROR: Entorno virtual no encontrado
goto end

:end
echo [%time%] Script terminado >> %LOG_FILE%
