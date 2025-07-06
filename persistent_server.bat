@echo off
REM Script de arranque PERSISTENTE - mantiene el servidor ejecutándose

set LOG_FILE=C:\Users\yessi\bar-code-scaner\persistent_startup.log
set PROJECT_DIR=C:\Users\yessi\bar-code-scaner

echo ================================== > %LOG_FILE%
echo SCANNER SERVER - ARRANQUE PERSISTENTE >> %LOG_FILE%
echo %date% %time% >> %LOG_FILE%
echo ================================== >> %LOG_FILE%

cd /d "%PROJECT_DIR%"

REM Verificaciones básicas
if not exist "server_https.py" goto error_file
if not exist ".venv\Scripts\python.exe" goto error_venv

echo [%time%] Archivos verificados >> %LOG_FILE%

REM Limpiar procesos anteriores
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

:restart_loop
echo [%time%] Iniciando servidor (intento) >> %LOG_FILE%

REM Ejecutar servidor con NOHUP para que persista
start "Scanner Server Persistent" /MIN cmd /c ".venv\Scripts\python.exe server_https.py >> %LOG_FILE% 2>&1"

REM Esperar arranque
timeout /t 15 >nul

REM Verificar si está funcionando
curl -k https://localhost:5443/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [%time%] SERVIDOR FUNCIONANDO >> %LOG_FILE%
    echo ✅ SERVIDOR FUNCIONANDO
    
    REM Verificar cada 30 segundos que sigue funcionando
    :monitor_loop
    timeout /t 30 >nul
    curl -k https://localhost:5443/ >nul 2>&1
    if %errorlevel% equ 0 (
        echo [%time%] Servidor OK - monitoreando >> %LOG_FILE%
        goto monitor_loop
    ) else (
        echo [%time%] SERVIDOR CAÍDO - reiniciando >> %LOG_FILE%
        goto restart_loop
    )
) else (
    echo [%time%] SERVIDOR NO RESPONDE - reintentando en 10s >> %LOG_FILE%
    timeout /t 10 >nul
    goto restart_loop
)

:error_file
echo [%time%] ERROR: server_https.py no encontrado >> %LOG_FILE%
exit /b 1

:error_venv
echo [%time%] ERROR: Entorno virtual no encontrado >> %LOG_FILE%
exit /b 1
