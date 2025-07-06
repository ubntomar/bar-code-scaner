@echo off
REM Script para instalar el servidor como servicio de Windows

echo 🔧 INSTALANDO COMO SERVICIO DE WINDOWS
echo =======================================
echo.

echo Este método es más avanzado y requiere permisos de administrador.
echo El servicio se ejecutará en segundo plano sin ventana visible.
echo.

echo 📦 Instalando dependencias necesarias...
.venv\Scripts\pip.exe install pywin32

if %errorlevel% neq 0 (
    echo ❌ Error instalando pywin32
    pause
    exit /b 1
)

echo.
echo 🔧 Instalando servicio...
.venv\Scripts\python.exe scanner_service.py install

if %errorlevel% equ 0 (
    echo ✅ Servicio instalado exitosamente
    echo.
    echo 🚀 Iniciando servicio...
    .venv\Scripts\python.exe scanner_service.py start
    
    if %errorlevel% equ 0 (
        echo ✅ Servicio iniciado exitosamente
        echo.
        echo 🎉 CONFIGURACION COMPLETADA
        echo ===========================
        echo ✅ El servidor se ejecuta como servicio de Windows
        echo 📍 Nombre: Scanner Server - Códigos de Barras
        echo.
        echo 💡 Para administrar el servicio:
        echo    - Abrir "Servicios" en Windows
        echo    - Buscar: Scanner Server - Códigos de Barras
        echo.
        echo 🔧 Para desinstalar:
        echo    .venv\Scripts\python.exe scanner_service.py remove
        echo.
    ) else (
        echo ❌ Error iniciando servicio
    )
) else (
    echo ❌ Error instalando servicio
    echo 💡 Ejecuta este script como Administrador
)

pause
