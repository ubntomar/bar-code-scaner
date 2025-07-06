@echo off
REM Script de diagnóstico mejorado para el arranque automático
REM Registra todo en un archivo de log para debugging

set LOG_FILE=C:\Users\yessi\bar-code-scaner\autostart_debug.log

echo ================================== >> %LOG_FILE%
echo DIAGNOSTICO ARRANQUE AUTOMATICO >> %LOG_FILE%
echo Fecha y hora: %date% %time% >> %LOG_FILE%
echo ================================== >> %LOG_FILE%

echo 🔍 DIAGNOSTICANDO ARRANQUE AUTOMATICO
echo =====================================
echo Creando log de diagnóstico en: %LOG_FILE%
echo.

REM Verificar directorio actual
echo [DEBUG] Directorio inicial: %cd% >> %LOG_FILE%
echo [INFO] Cambiando a directorio del proyecto... >> %LOG_FILE%

cd /d "C:\Users\yessi\bar-code-scaner"
echo [DEBUG] Directorio después de cd: %cd% >> %LOG_FILE%

REM Verificar archivos necesarios
if exist "server_https.py" (
    echo [OK] server_https.py encontrado >> %LOG_FILE%
    echo ✅ server_https.py encontrado
) else (
    echo [ERROR] server_https.py NO encontrado >> %LOG_FILE%
    echo ❌ ERROR: server_https.py NO encontrado
    echo Directorio actual: %cd%
    pause
    exit /b 1
)

if exist ".venv\Scripts\python.exe" (
    echo [OK] Python del entorno virtual encontrado >> %LOG_FILE%
    echo ✅ Entorno virtual encontrado
) else (
    echo [ERROR] .venv\Scripts\python.exe NO encontrado >> %LOG_FILE%
    echo ❌ ERROR: Entorno virtual NO encontrado
    pause
    exit /b 1
)

REM Verificar dependencias críticas
echo [INFO] Verificando dependencias... >> %LOG_FILE%
.venv\Scripts\python.exe -c "import flask; print('Flask OK')" >> %LOG_FILE% 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Flask no disponible >> %LOG_FILE%
    echo ❌ ERROR: Flask no disponible
    pause
    exit /b 1
)

echo ✅ Dependencias básicas OK
echo [INFO] Dependencias básicas verificadas >> %LOG_FILE%

REM Intentar ejecutar el servidor con captura de errores
echo [INFO] Iniciando servidor... >> %LOG_FILE%
echo ⏳ Iniciando servidor...

.venv\Scripts\python.exe server_https.py >> %LOG_FILE% 2>&1

REM Capturar código de salida
set EXIT_CODE=%errorlevel%
echo [INFO] Servidor terminó con código: %EXIT_CODE% >> %LOG_FILE%

if %EXIT_CODE% neq 0 (
    echo ❌ El servidor terminó con errores (código: %EXIT_CODE%)
    echo Revisa el log: %LOG_FILE%
) else (
    echo ℹ️ El servidor terminó normalmente
)

echo.
echo 📄 Log completo guardado en: %LOG_FILE%
echo ⏳ Presiona cualquier tecla para ver el log...
pause > nul

REM Mostrar el log
type %LOG_FILE%

echo.
echo ⏳ Presiona cualquier tecla para cerrar...
pause > nul

setup_autostart.bat
