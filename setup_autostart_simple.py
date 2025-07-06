#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Python para configurar arranque automático sin necesidad de permisos de administrador
Usa la carpeta de inicio de Windows
"""

import os
import shutil
import sys
from pathlib import Path

def setup_autostart():
    """Configurar arranque automático usando la carpeta Startup de Windows"""
    
    print("🔧 CONFIGURANDO ARRANQUE AUTOMATICO (SIN ADMIN)")
    print("=" * 50)
    
    # Rutas
    project_dir = Path(__file__).parent
    startup_folder = Path(os.path.expanduser("~")) / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
    
    # Script que se ejecutará
    bat_content = f"""@echo off
cd /d "{project_dir}"
.venv\\Scripts\\python.exe server_https.py
"""
    
    # Crear archivo .bat en la carpeta de inicio
    startup_script = startup_folder / "Scanner_Server_AutoStart.bat"
    
    try:
        # Crear directorio si no existe
        startup_folder.mkdir(parents=True, exist_ok=True)
        
        # Escribir el script
        with open(startup_script, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        print(f"✅ Script creado en: {startup_script}")
        print("✅ El servidor se iniciará automáticamente al arrancar Windows")
        print()
        print("💡 Para desactivar:")
        print(f"   Elimina el archivo: {startup_script}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def remove_autostart():
    """Remover arranque automático"""
    startup_folder = Path(os.path.expanduser("~")) / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
    startup_script = startup_folder / "Scanner_Server_AutoStart.bat"
    
    try:
        if startup_script.exists():
            startup_script.unlink()
            print("✅ Arranque automático desactivado")
        else:
            print("ℹ️ No hay arranque automático configurado")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_autostart()
    else:
        setup_autostart()

if __name__ == "__main__":
    main()
