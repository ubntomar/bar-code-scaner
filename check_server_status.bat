@echo off
REM Script para verificar el estado del servidor

echo 🔍 VERIFICANDO ESTADO DEL SERVIDOR
echo ==================================
echo.

REM Verificar procesos Python
echo 📊 Procesos Python activos:
tasklist | findstr python.exe
if %errorlevel% neq 0 (
    echo   Ningún proceso Python ejecutándose
)

echo.

REM Verificar puerto 5443
echo 🌐 Verificando puerto 5443:
netstat -an | findstr :5443
if %errorlevel% neq 0 (
    echo   Puerto 5443 no está en uso
) else (
    echo   ✅ Puerto 5443 está siendo usado
)

echo.

REM Probar conexión HTTP
echo 🌐 Probando conexión al servidor...
curl -k https://localhost:5443/ > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SERVIDOR FUNCIONANDO CORRECTAMENTE
    echo 🌐 URL: https://localhost:5443/
) else (
    echo ❌ Servidor no responde
    echo.
    echo 💡 Para iniciar el servidor manualmente:
    echo    .\auto_start_server.bat
)

echo.

REM Mostrar log si existe
if exist "server_startup.log" (
    echo 📄 ÚLTIMAS LÍNEAS DEL LOG:
    echo ------------------------
    for /f "tokens=*" %%a in ('more +0 server_startup.log') do (
        echo %%a
    )
) else (
    echo 📄 No hay archivo de log disponible
)

echo.
pause
