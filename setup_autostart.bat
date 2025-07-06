@echo off
REM Script para configurar arranque automático del servidor

echo 🔧 CONFIGURANDO ARRANQUE AUTOMATICO
echo ====================================
echo.

echo Este script creará una tarea programada que iniciará
echo el servidor automáticamente cuando Windows arranque.
echo.

set TASK_NAME=Scanner_Server_AutoStart
set SCRIPT_PATH=%~dp0persistent_server.bat

echo 📝 Creando tarea programada...
echo Nombre de tarea: %TASK_NAME%
echo Script a ejecutar: %SCRIPT_PATH%
echo.

REM Eliminar tarea existente si existe
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Crear nueva tarea programada
schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_PATH%\"" /sc onstart /ru "%USERNAME%" /f

if %errorlevel% equ 0 (
    echo ✅ Tarea programada creada exitosamente
    echo.
    echo 🎉 CONFIGURACION COMPLETADA
    echo ===========================
    echo ✅ El servidor se iniciará automáticamente al arrancar Windows
    echo 📍 Nombre de la tarea: %TASK_NAME%
    echo.
    echo 💡 Para administrar la tarea:
    echo    - Abrir "Programador de tareas" en Windows
    echo    - Buscar: %TASK_NAME%
    echo.
    echo 🔧 Para desactivar el arranque automático:
    echo    schtasks /delete /tn "%TASK_NAME%" /f
    echo.
) else (
    echo ❌ Error al crear la tarea programada
    echo 💡 Ejecuta este script como Administrador
    echo.
)

pause
