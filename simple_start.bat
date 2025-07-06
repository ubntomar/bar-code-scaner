@echo off
REM Script simple y robusto para arranque automático

echo ========================================
echo     SCANNER SERVER - ARRANQUE AUTO
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\Users\yessi\bar-code-scaner"

REM Verificar archivos básicos
if not exist "server_https.py" (
    echo ERROR: server_https.py no encontrado
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Entorno virtual no encontrado
    pause
    exit /b 1
)

echo Archivos verificados OK
echo.

REM Limpiar procesos previos
taskkill /f /im python.exe >nul 2>&1

REM Esperar un momento
timeout /t 2 >nul

echo Iniciando servidor...
echo.

REM Ejecutar servidor con timeout para evitar colgarse
start "Scanner Server" /MIN .venv\Scripts\python.exe server_https.py

REM Esperar que arranque
timeout /t 8 >nul

REM Verificar si funciona
echo Verificando servidor...
curl -k https://localhost:5443/ >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ✅ SERVIDOR FUNCIONANDO
    echo URL: https://localhost:5443/
    start https://localhost:5443/
) else (
    echo.
    echo ❌ Servidor no responde
    echo Revisa si hay errores en la ventana del servidor
)

echo.
echo Presiona CTRL+C para salir cuando termines
timeout /t 5 >nul
