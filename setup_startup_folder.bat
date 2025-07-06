@echo off
REM Script para agregar el servidor a la carpeta de inicio de Windows

echo 🔧 CONFIGURANDO ARRANQUE AUTOMATICO - METODO STARTUP
echo =====================================================
echo.

REM Obtener ruta de la carpeta de inicio
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SCRIPT_PATH=%~dp0auto_start_server.bat
set SHORTCUT_NAME=Scanner Server AutoStart.lnk

echo 📁 Carpeta de inicio: %STARTUP_FOLDER%
echo 📝 Script a ejecutar: %SCRIPT_PATH%
echo.

REM Crear acceso directo usando PowerShell
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Scanner Server Auto Start'; $Shortcut.Save()}"

if exist "%STARTUP_FOLDER%\%SHORTCUT_NAME%" (
    echo ✅ Acceso directo creado exitosamente
    echo.
    echo 🎉 CONFIGURACION COMPLETADA
    echo ===========================
    echo ✅ El servidor se iniciará automáticamente al iniciar sesión
    echo 📍 Ubicación: %STARTUP_FOLDER%
    echo 📝 Acceso directo: %SHORTCUT_NAME%
    echo.
    echo 💡 Para desactivar:
    echo    Elimina el archivo: "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
    echo.
) else (
    echo ❌ Error al crear el acceso directo
    echo.
)

pause
