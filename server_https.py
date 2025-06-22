#!/usr/bin/env python3
"""
Scanner Server HTTPS - Servidor seguro SOLO HTTPS para acceso completo a cámara móvil
Compatible con Ubuntu y Windows - Con gestión inteligente de foco de ventanas
NUEVA FUNCIONALIDAD: Sistema de códigos con imágenes asociadas
"""

from flask import Flask, render_template, request, jsonify
import base64
import io
from PIL import Image
import threading
import time
import socket
import ssl
import os
from datetime import datetime, timedelta

# Importar módulos locales
from scanner import BarcodeScanner
from keyboard_sim import KeyboardSimulator
from database import ImageDatabase

app = Flask(__name__)

# Inicializar componentes
scanner = BarcodeScanner()
keyboard = KeyboardSimulator()
image_db = ImageDatabase()

# Configuración
CONFIG = {
    'host': '0.0.0.0',
    'https_port': 5443,
    'debug': False,
    'auto_type': True,
    'add_enter': True
}

def create_self_signed_cert():
    """Crear certificado autofirmado para HTTPS"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        import ipaddress
        
        print("🔐 Creando certificado SSL autofirmado...")
        
        # Generar clave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Obtener IP local
        local_ip = get_local_ip()
        
        # Crear certificado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CO"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Meta"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Castilla La Nueva"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Scanner Server"),
            x509.NameAttribute(NameOID.COMMON_NAME, local_ip),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("scanner-server.local"),
                x509.IPAddress(ipaddress.ip_address(local_ip)),
                x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Guardar certificado y clave
        cert_dir = "ssl_certs"
        os.makedirs(cert_dir, exist_ok=True)
        
        cert_path = os.path.join(cert_dir, "server.crt")
        key_path = os.path.join(cert_dir, "server.key")
        
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print(f"✅ Certificado creado: {cert_path}")
        print(f"✅ Clave privada creada: {key_path}")
        
        return cert_path, key_path
        
    except ImportError:
        print("⚠️ cryptography no instalada. Usando certificado básico...")
        return create_basic_cert()
    except Exception as e:
        print(f"❌ Error creando certificado: {e}")
        return create_basic_cert()

def create_basic_cert():
    """Crear certificado básico usando OpenSSL"""
    try:
        cert_dir = "ssl_certs"
        os.makedirs(cert_dir, exist_ok=True)
        
        cert_path = os.path.join(cert_dir, "server.crt")
        key_path = os.path.join(cert_dir, "server.key")
        
        local_ip = get_local_ip()
        
        # Comando OpenSSL para crear certificado
        openssl_cmd = f"""
openssl req -x509 -newkey rsa:4096 -keyout {key_path} -out {cert_path} \
-days 365 -nodes -subj "/C=CO/ST=Meta/L=Castilla/O=ScannerServer/CN={local_ip}" \
-addext "subjectAltName=DNS:localhost,IP:{local_ip},IP:127.0.0.1"
"""
        
        import subprocess
        result = subprocess.run(openssl_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Certificado creado con OpenSSL")
            return cert_path, key_path
        else:
            print(f"❌ Error con OpenSSL: {result.stderr}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error creando certificado básico: {e}")
        return None, None

def get_local_ip():
    """Obtener la IP local para mostrar al usuario"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.100"

@app.route('/')
def index():
    """Página principal con interfaz de escaneo"""
    return render_template('scanner.html')

@app.route('/scan', methods=['POST'])
def scan_barcode():
    """Endpoint para procesar imágenes y extraer códigos de barras"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No se encontró imagen en la petición'}), 400
        
        # Decodificar imagen base64
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Convertir a PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Escanear códigos de barras
        barcodes = scanner.scan_image(image)
        
        if not barcodes:
            return jsonify({
                'success': False,
                'message': 'No se encontraron códigos de barras',
                'barcodes': []
            })
        
        # Procesar el primer código encontrado
        barcode_data = barcodes[0]
        code_value = barcode_data['data']
        code_type = barcode_data['type']
        
        # Auto-escribir si está habilitado
        if CONFIG['auto_type']:
            def type_code():
                # Pequeña pausa para que la respuesta llegue al navegador
                time.sleep(0.2)
                
                # Usar el workflow completo con gestión de foco
                success = keyboard.scan_and_type_workflow(code_value)
                
                if CONFIG['add_enter'] and success:
                    # Pequeña pausa antes del Enter
                    time.sleep(0.1)
                    keyboard.press_enter()
                
                if success:
                    print(f"✅ Código {code_type} escrito correctamente: {code_value}")
                else:
                    print(f"⚠️ Problemas escribiendo código: {code_value}")
            
            threading.Thread(target=type_code, daemon=True).start()
        
        return jsonify({
            'success': True,
            'message': f'Código {code_type} escaneado correctamente',
            'barcodes': barcodes,
            'auto_typed': CONFIG['auto_type'],
            'focus_managed': keyboard.get_status().get('focus_management', False)
        })
        
    except Exception as e:
        print(f"Error al procesar imagen: {str(e)}")
        return jsonify({'error': f'Error al procesar imagen: {str(e)}'}), 500

@app.route('/guardar-imagen', methods=['POST'])
def guardar_imagen():
    """Endpoint para guardar imagen asociada a código"""
    try:
        data = request.get_json()
        
        if 'codigo' not in data or 'imagen' not in data:
            return jsonify({'error': 'Faltan datos: código e imagen requeridos'}), 400
        
        codigo = data['codigo']
        imagen_base64 = data['imagen']
        dispositivo = data.get('dispositivo', 'Scanner Web')
        
        # Guardar en base de datos
        success = image_db.save_image(codigo, imagen_base64, dispositivo)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Imagen guardada para código: {codigo}',
                'codigo': codigo
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error guardando imagen en base de datos'
            }), 500
            
    except Exception as e:
        print(f"Error guardando imagen: {str(e)}")
        return jsonify({'error': f'Error guardando imagen: {str(e)}'}), 500

@app.route('/buscar')
def buscar_page():
    """Página de búsqueda de imágenes por código"""
    return render_template('buscar.html')

@app.route('/api/buscar/<codigo>')
def buscar_imagen_api(codigo):
    """API para buscar imagen por código"""
    try:
        resultado = image_db.get_image(codigo)
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error buscando imagen para {codigo}: {str(e)}")
        return jsonify({
            'codigo': codigo,
            'encontrada': False,
            'error': str(e)
        }), 500

@app.route('/api/estadisticas')
def estadisticas_api():
    """API para obtener estadísticas de la base de datos"""
    try:
        stats = image_db.get_statistics()
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recientes')
def recientes_api():
    """API para obtener códigos recientes con opción de incluir imágenes"""
    try:
        limit = request.args.get('limit', 200, type=int)
        include_images = request.args.get('include_images', 'false').lower() == 'true'
        
        recientes = image_db.get_recent_codes(limit, include_images)
        return jsonify(recientes)
        
    except Exception as e:
        print(f"Error obteniendo códigos recientes: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/buscar-coincidencias/<search_term>')
def buscar_coincidencias_api(search_term):
    """API para buscar códigos que contengan el término"""
    try:
        resultados = image_db.search_codes(search_term)
        return jsonify(resultados)
        
    except Exception as e:
        print(f"Error buscando coincidencias para '{search_term}': {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Endpoint para configuración del servidor"""
    if request.method == 'GET':
        return jsonify(CONFIG)
    
    elif request.method == 'POST':
        data = request.get_json()
        for key, value in data.items():
            if key in CONFIG:
                CONFIG[key] = value
        return jsonify({'success': True, 'config': CONFIG})

@app.route('/status')
def status():
    """Estado del servidor"""
    db_stats = image_db.get_statistics()
    return jsonify({
        'status': 'running',
        'scanner_ready': scanner.is_ready(),
        'keyboard_ready': keyboard.is_ready(),
        'server_type': 'HTTPS only',
        'config': CONFIG,
        'keyboard_status': keyboard.get_status(),
        'database_stats': db_stats
    })

@app.route('/prepare-focus', methods=['POST'])
def prepare_focus():
    """Preparar el sistema recordando la ventana activa actual"""
    try:
        success = keyboard.remember_active_window()
        status = keyboard.get_status()
        
        return jsonify({
            'success': success,
            'message': 'Ventana activa recordada' if success else 'No se pudo recordar ventana',
            'current_window': status.get('current_window'),
            'focus_management_available': status.get('focus_management', False)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/window-info')
def window_info():
    """Obtener información de la ventana actualmente activa"""
    try:
        current_window = keyboard.get_current_window_info()
        status = keyboard.get_status()
        
        return jsonify({
            'current_window': current_window,
            'remembered_window': status.get('remembered_window'),
            'focus_management_available': status.get('focus_management', False)
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

def install_certificate_instructions(cert_path, local_ip, https_port):
    """Mostrar instrucciones para instalar certificado"""
    print("\n" + "="*60)
    print("📱 INSTRUCCIONES PARA USAR LA CÁMARA EN MÓVIL")
    print("="*60)
    print(f"""
1️⃣  ACCEDE A LA URL HTTPS:
   https://{local_ip}:{https_port}

2️⃣  EL NAVEGADOR MOSTRARÁ "NO SEGURO":
   - Chrome: Presiona "Avanzado" → "Ir a {local_ip} (no seguro)"
   - Firefox: Presiona "Avanzado" → "Aceptar el riesgo y continuar"
   - Safari: Presiona "Detalles" → "Visitar este sitio web"

3️⃣  PERMITIR CÁMARA:
   - El navegador preguntará sobre permisos de cámara
   - Presiona "Permitir" o "Allow"

4️⃣  ¡LISTO! Ahora puedes usar la cámara normalmente

⚠️  IMPORTANTE:
   - Esto es un certificado autofirmado (seguro pero no verificado)
   - Solo funciona en tu red local
   - El navegador puede mostrar advertencias (es normal)
   - Se requiere HTTPS para acceso completo a la cámara móvil

🎯  NUEVA FUNCIÓN - GESTIÓN INTELIGENTE DE FOCO:
   - El sistema recordará automáticamente dónde tienes el cursor
   - Los códigos se escribirán en tu editor, no en Firefox
   - También puedes usar el botón "🎯 Preparar Foco" manualmente

📸  NUEVA FUNCIÓN - SISTEMA DE IMÁGENES:
   - Conteo regresivo de 2 segundos tras escaneo exitoso
   - Captura automática de imagen asociada al código
   - Búsqueda instantánea desde cualquier PC en /buscar
   - Base de datos SQLite local para almacenamiento
""")
    print("="*60)

def run_https_server():
    """Ejecutar servidor HTTPS solamente"""
    local_ip = get_local_ip()
    
    # Crear certificados SSL
    cert_path, key_path = create_self_signed_cert()
    
    if not cert_path or not key_path:
        print("\n❌ ERROR: No se pudieron crear los certificados SSL")
        print("💡 Solución: Ejecuta primero ./setup_https.sh")
        return
    
    print("🚀 SCANNER SERVER HTTPS CON GESTIÓN DE FOCO E IMÁGENES INICIADO")
    print("="*70)
    print(f"🔒 URL del servidor: https://{local_ip}:{CONFIG['https_port']}")
    print(f"🔍 URL de búsqueda: https://{local_ip}:{CONFIG['https_port']}/buscar")
    print("🎯 Nueva función: Gestión inteligente de foco de ventanas")
    print("📸 Nueva función: Sistema de códigos con imágenes asociadas")
    print("="*70)
    
    # Mostrar instrucciones
    install_certificate_instructions(cert_path, local_ip, CONFIG['https_port'])
    
    # Ejecutar servidor HTTPS
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        
        print("✅ Certificados SSL cargados correctamente")
        print("🎯 Sistema de foco inteligente activado")
        print("📸 Sistema de imágenes inicializado")
        print("🌐 Servidor iniciando...")
        print(f"📱 Accede desde tu móvil: https://{local_ip}:{CONFIG['https_port']}")
        print(f"🔍 Búsqueda de imágenes: https://{local_ip}:{CONFIG['https_port']}/buscar")
        print("\n⏹️  Presiona Ctrl+C para detener")
        
        app.run(
            host=CONFIG['host'],
            port=CONFIG['https_port'],
            debug=CONFIG['debug'],
            ssl_context=context,
            threaded=True
        )
        
    except Exception as e:
        print(f"\n❌ Error iniciando servidor HTTPS: {e}")
        print("💡 Verifica que el puerto 5443 esté libre")

if __name__ == '__main__':
    try:
        run_https_server()
    except KeyboardInterrupt:
        print("\n👋 Cerrando servidor HTTPS...")
    except Exception as e:
        print(f"\n❌ Error ejecutando servidor: {e}")
        print("💡 Verifica:")
        print("   1. Que los certificados SSL estén creados")
        print("   2. Que el puerto 5443 esté libre")
        print("   3. Ejecutar ./setup_https.sh si es necesario")