#!/usr/bin/env python3
"""
Script para probar el servidor y capturar errores específicos
"""

import sys
import os
import traceback

def test_imports():
    """Probar todas las importaciones necesarias"""
    print("🔍 PROBANDO IMPORTACIONES...")
    
    modules = [
        'flask', 'PIL', 'pyzbar', 'numpy', 'requests', 
        'cryptography', 'ssl', 'threading', 'time', 'socket'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    return True

def test_local_modules():
    """Probar módulos locales del proyecto"""
    print("\n🔍 PROBANDO MÓDULOS LOCALES...")
    
    try:
        from scanner import BarcodeScanner
        print("✅ scanner.py")
    except Exception as e:
        print(f"❌ scanner.py: {e}")
        return False
        
    try:
        from keyboard_sim import KeyboardSimulator
        print("✅ keyboard_sim.py")
    except Exception as e:
        print(f"❌ keyboard_sim.py: {e}")
        return False
        
    try:
        from database import ImageDatabase
        print("✅ database.py")
    except Exception as e:
        print(f"❌ database.py: {e}")
        return False
        
    return True

def test_ssl_certificates():
    """Verificar certificados SSL"""
    print("\n🔍 PROBANDO CERTIFICADOS SSL...")
    
    cert_files = [
        'ssl_certs/server.crt',
        'ssl_certs/server.key'
    ]
    
    for cert_file in cert_files:
        if os.path.exists(cert_file):
            print(f"✅ {cert_file}")
        else:
            print(f"❌ {cert_file} no encontrado")
            return False
    return True

def test_server_startup():
    """Probar arranque del servidor sin ejecutarlo"""
    print("\n🔍 PROBANDO CONFIGURACIÓN DEL SERVIDOR...")
    
    try:
        # Importar Flask
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask app creada")
        
        # Probar SSL context
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('ssl_certs/server.crt', 'ssl_certs/server.key')
        print("✅ SSL context creado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        traceback.print_exc()
        return False

def main():
    print("🧪 DIAGNÓSTICO COMPLETO DEL SERVIDOR")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Probar importaciones
    if not test_imports():
        all_tests_passed = False
    
    # Probar módulos locales
    if not test_local_modules():
        all_tests_passed = False
    
    # Probar certificados SSL
    if not test_ssl_certificates():
        all_tests_passed = False
    
    # Probar configuración del servidor
    if not test_server_startup():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ TODOS LOS TESTS PASARON")
        print("🚀 El servidor debería poder arrancar")
        print("\n💡 Para iniciar manualmente:")
        print("   .venv\\Scripts\\python.exe server_https.py")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Corrige los errores antes de arrancar el servidor")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
