#!/usr/bin/env python3
"""
Sistema de Base de Datos SQLite para gestión de códigos e imágenes
Mantiene la relación código-imagen con sobrescritura automática
"""

import sqlite3
import logging
import threading
import base64
from datetime import datetime
import os

class ImageDatabase:
    """Clase para gestionar la base de datos de códigos e imágenes"""
    
    def __init__(self, db_path="scanner_database.db"):
        """Inicializar base de datos"""
        self.db_path = db_path
        self.lock = threading.Lock()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Inicializar base de datos
        self.init_database()
        self.logger.info(f"Base de datos inicializada: {self.db_path}")
    
    def init_database(self):
        """Crear tabla si no existe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Crear tabla principal
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS codigos_imagenes (
                        codigo TEXT PRIMARY KEY,
                        imagen_blob BLOB NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        tamaño_kb INTEGER,
                        dispositivo TEXT
                    )
                ''')
                
                # Crear índice para búsquedas rápidas
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON codigos_imagenes(timestamp)
                ''')
                
                conn.commit()
                self.logger.info("✅ Tabla de códigos creada/verificada")
                
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def save_image(self, codigo, imagen_base64, dispositivo="Scanner"):
        """Guardar imagen asociada a código (sobrescribe si existe)"""
        with self.lock:
            try:
                # Decodificar base64 a bytes
                if imagen_base64.startswith('data:image'):
                    imagen_base64 = imagen_base64.split(',')[1]
                
                imagen_bytes = base64.b64decode(imagen_base64)
                tamaño_kb = len(imagen_bytes) // 1024
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Insertar o actualizar (REPLACE sobrescribe automáticamente)
                    cursor.execute('''
                        REPLACE INTO codigos_imagenes 
                        (codigo, imagen_blob, timestamp, tamaño_kb, dispositivo)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (codigo, imagen_bytes, datetime.now(), tamaño_kb, dispositivo))
                    
                    conn.commit()
                    
                    self.logger.info(f"✅ Imagen guardada: {codigo} ({tamaño_kb} KB)")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Error guardando imagen {codigo}: {e}")
                return False
    
    def get_image(self, codigo):
        """Recuperar imagen por código"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT imagen_blob, timestamp, tamaño_kb, dispositivo
                    FROM codigos_imagenes 
                    WHERE codigo = ?
                ''', (codigo,))
                
                result = cursor.fetchone()
                
                if result:
                    imagen_bytes, timestamp, tamaño_kb, dispositivo = result
                    
                    # Convertir bytes a base64
                    imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                    imagen_data_url = f"data:image/jpeg;base64,{imagen_base64}"
                    
                    return {
                        'codigo': codigo,
                        'imagen': imagen_data_url,
                        'timestamp': timestamp,
                        'tamaño_kb': tamaño_kb,
                        'dispositivo': dispositivo,
                        'encontrada': True
                    }
                else:
                    return {
                        'codigo': codigo,
                        'encontrada': False
                    }
                    
        except Exception as e:
            self.logger.error(f"Error recuperando imagen {codigo}: {e}")
            return {
                'codigo': codigo,
                'encontrada': False,
                'error': str(e)
            }
    
    

    def get_recent_codes(self, limit=200, include_images=False):
        """Obtener códigos recientes con opción de incluir imágenes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if include_images:
                    # Incluir imágenes para vista previa
                    cursor.execute('''
                        SELECT codigo, timestamp, tamaño_kb, dispositivo, imagen_blob
                        FROM codigos_imagenes 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                    
                    results = cursor.fetchall()
                    
                    return [{
                        'codigo': row[0],
                        'timestamp': row[1],
                        'tamaño_kb': row[2],
                        'dispositivo': row[3],
                        'imagen_miniatura': self._create_thumbnail(row[4]) if row[4] else None
                    } for row in results]
                else:
                    # Versión original sin imágenes
                    cursor.execute('''
                        SELECT codigo, timestamp, tamaño_kb, dispositivo
                        FROM codigos_imagenes 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                    
                    results = cursor.fetchall()
                    
                    return [{
                        'codigo': row[0],
                        'timestamp': row[1],
                        'tamaño_kb': row[2],
                        'dispositivo': row[3]
                    } for row in results]
                    
        except Exception as e:
            self.logger.error(f"Error obteniendo códigos recientes: {e}")
            return []

    def _create_thumbnail(self, imagen_bytes):
        """Crear miniatura de imagen para vista previa"""
        try:
            if not imagen_bytes:
                return None
                
            # Convertir bytes a base64 para miniatura
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
            imagen_data_url = f"data:image/jpeg;base64,{imagen_base64}"
            
            return imagen_data_url
            
        except Exception as e:
            self.logger.debug(f"Error creando miniatura: {e}")
            return None


    def get_statistics(self):
        """Obtener estadísticas de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de códigos
                cursor.execute('SELECT COUNT(*) FROM codigos_imagenes')
                total_codes = cursor.fetchone()[0]
                
                # Tamaño total
                cursor.execute('SELECT SUM(tamaño_kb) FROM codigos_imagenes')
                total_size_kb = cursor.fetchone()[0] or 0
                
                # Código más reciente
                cursor.execute('''
                    SELECT codigo, timestamp FROM codigos_imagenes 
                    ORDER BY timestamp DESC LIMIT 1
                ''')
                last_code_result = cursor.fetchone()
                last_code = last_code_result[0] if last_code_result else "N/A"
                last_timestamp = last_code_result[1] if last_code_result else "N/A"
                
                return {
                    'total_codes': total_codes,
                    'total_size_kb': total_size_kb,
                    'total_size_mb': round(total_size_kb / 1024, 2),
                    'last_code': last_code,
                    'last_timestamp': last_timestamp,
                    'db_file_size_mb': round(os.path.getsize(self.db_path) / (1024*1024), 2) if os.path.exists(self.db_path) else 0
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_codes': 0,
                'total_size_kb': 0,
                'total_size_mb': 0,
                'last_code': 'Error',
                'last_timestamp': 'Error',
                'db_file_size_mb': 0
            }
    
    def search_codes(self, search_term):
        """Buscar códigos que contengan el término"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT codigo, timestamp, tamaño_kb, dispositivo
                    FROM codigos_imagenes 
                    WHERE codigo LIKE ?
                    ORDER BY timestamp DESC
                ''', (f'%{search_term}%',))
                
                results = cursor.fetchall()
                
                return [{
                    'codigo': row[0],
                    'timestamp': row[1],
                    'tamaño_kb': row[2],
                    'dispositivo': row[3]
                } for row in results]
                
        except Exception as e:
            self.logger.error(f"Error buscando códigos con '{search_term}': {e}")
            return []
    
    def delete_image(self, codigo):
        """Eliminar imagen por código"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM codigos_imagenes WHERE codigo = ?', (codigo,))
                    deleted_rows = cursor.rowcount
                    conn.commit()
                    
                    if deleted_rows > 0:
                        self.logger.info(f"✅ Imagen eliminada: {codigo}")
                        return True
                    else:
                        self.logger.warning(f"⚠️ No se encontró código para eliminar: {codigo}")
                        return False
                        
            except Exception as e:
                self.logger.error(f"Error eliminando imagen {codigo}: {e}")
                return False
    
    def cleanup_old_images(self, days_old=30):
        """Limpiar imágenes antiguas (opcional)"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        DELETE FROM codigos_imagenes 
                        WHERE timestamp < datetime('now', '-' || ? || ' days')
                    ''', (days_old,))
                    
                    deleted_rows = cursor.rowcount
                    conn.commit()
                    
                    if deleted_rows > 0:
                        self.logger.info(f"🧹 Limpieza: {deleted_rows} imágenes antiguas eliminadas")
                    
                    return deleted_rows
                    
            except Exception as e:
                self.logger.error(f"Error en limpieza de imágenes: {e}")
                return 0
    
    def close(self):
        """Cerrar conexión (normalmente no necesario con context managers)"""
        self.logger.info("Base de datos cerrada")
    
    def test_database(self):
        """Test básico de la base de datos"""
        try:
            # Test de escritura
            test_codigo = "TEST123"
            test_imagen = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA="
            
            result = self.save_image(test_codigo, test_imagen, "Test")
            if not result:
                return False
            
            # Test de lectura
            retrieved = self.get_image(test_codigo)
            if not retrieved.get('encontrada'):
                return False
            
            # Test de estadísticas
            stats = self.get_statistics()
            if stats['total_codes'] < 1:
                return False
            
            # Limpiar test
            self.delete_image(test_codigo)
            
            self.logger.info("✅ Test de base de datos exitoso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Test de base de datos falló: {e}")
            return False