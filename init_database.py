#!/usr/bin/env python3
"""
Script de inicialización de la base de datos para Scanner Server
Crea y verifica la base de datos SQLite para el sistema de códigos con imágenes
"""

import os
import sys
from database import ImageDatabase

def main():
    print("🔧 INICIALIZANDO SISTEMA DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Crear instancia de base de datos
        print("📦 Creando base de datos...")
        db = ImageDatabase()
        
        # Verificar que la base de datos funciona
        print("🔍 Verificando funcionalidad...")
        if db.test_database():
            print("✅ Base de datos inicializada correctamente")
        else:
            print("❌ Error en la verificación de la base de datos")
            return 1
        
        # Mostrar estadísticas iniciales
        stats = db.get_statistics()
        print("\n📊 ESTADÍSTICAS INICIALES:")
        print(f"   Códigos almacenados: {stats['total_codes']}")
        print(f"   Tamaño base de datos: {stats['db_file_size_mb']} MB")
        
        if stats['total_codes'] > 0:
            print(f"   Último código: {stats['last_code']}")
            print(f"   Fecha último: {stats['last_timestamp']}")
        
        print("\n🎉 SISTEMA LISTO PARA USAR")
        print("=" * 50)
        print("✅ La base de datos está configurada y funcionando")
        print("📱 Inicia el servidor con: python3 server_https.py")
        print("🔍 Página de búsqueda: https://tu-ip:5443/buscar")
        print("📸 Las imágenes se guardarán automáticamente tras escanear")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR INICIALIZANDO BASE DE DATOS: {e}")
        print("\n💡 SOLUCIONES:")
        print("   1. Verificar permisos de escritura en el directorio")
        print("   2. Verificar que SQLite esté disponible")
        print("   3. Revisar el archivo database.py")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)