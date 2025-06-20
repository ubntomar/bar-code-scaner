#!/bin/bash

# Script para configurar servidor HTTPS para Scanner Server
# Permite acceso completo a la cámara móvil

set -e

echo "🔒 CONFIGURACIÓN HTTPS PARA SCANNER SERVER"
echo "==========================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "server.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio scanner_server"
    echo "   cd scanner_server && ./setup_https.sh"
    exit 1
fi

# Activar entorno virtual
if [ -d "venv" ]; then
    echo "🐍 Activando entorno virtual..."
    source venv/bin/activate
else
    echo "❌ Error: No se encontró entorno virtual. Ejecuta primero la instalación."
    exit 1
fi

echo "📦 Instalando dependencias para HTTPS..."

# Instalar OpenSSL si no está disponible
if ! command -v openssl &> /dev/null; then
    echo "📦 Instalando OpenSSL..."
    sudo apt-get update
    sudo apt-get install -y openssl
fi

# Instalar dependencias Python para certificados
echo "📦 Instalando cryptography..."
pip install cryptography pyopenssl

# Verificar instalación
echo "🔍 Verificando instalación..."

python3 -c "
try:
    import cryptography
    print('✅ cryptography instalado')
except ImportError:
    print('❌ Error: cryptography no instalado')

try:
    import OpenSSL
    print('✅ pyopenssl instalado')
except ImportError:
    print('❌ Error: pyopenssl no instalado')

try:
    import ssl
    print('✅ ssl disponible')
except ImportError:
    print('❌ Error: ssl no disponible')
"

# Crear directorio para certificados
mkdir -p ssl_certs

# Detectar IP local
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "🌐 IP local detectada: $LOCAL_IP"

# Crear archivo de configuración OpenSSL
cat > ssl_certs/openssl.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = CO
ST = Meta
L = Castilla La Nueva
O = Scanner Server
CN = $LOCAL_IP

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = scanner-server.local
IP.1 = $LOCAL_IP
IP.2 = 127.0.0.1
EOF

echo "📋 Configuración OpenSSL creada"

# Crear certificado autofirmado usando OpenSSL
echo "🔐 Creando certificado SSL..."

openssl req -x509 -newkey rsa:4096 -keyout ssl_certs/server.key -out ssl_certs/server.crt \
-days 365 -nodes -config ssl_certs/openssl.conf -extensions v3_req

if [ $? -eq 0 ]; then
    echo "✅ Certificado SSL creado exitosamente"
    
    # Verificar certificado
    echo "🔍 Verificando certificado..."
    openssl x509 -in ssl_certs/server.crt -text -noout | grep -A 3 "Subject Alternative Name" || echo "Certificado básico creado"
    
    echo ""
    echo "📁 Archivos creados:"
    ls -la ssl_certs/
    
else
    echo "❌ Error creando certificado"
    exit 1
fi

# Actualizar requirements.txt con dependencias HTTPS
echo "📝 Actualizando requirements.txt..."

cat > requirements.txt << 'EOF'
flask==2.3.3
pyzbar==0.1.9
pynput==1.7.6
pillow==10.0.1
requests==2.31.0
cryptography>=3.4.8
pyopenssl>=21.0.0
EOF

echo "✅ requirements.txt actualizado"

# Crear script de ejecución HTTPS
cat > run_https_server.sh << 'EOF'
#!/bin/bash
echo "🔒 Iniciando Scanner Server HTTPS..."
source venv/bin/activate
python3 server_https.py
EOF

chmod +x run_https_server.sh

echo ""
echo "🎉 CONFIGURACIÓN HTTPS COMPLETADA"
echo "================================="
echo ""
echo "🚀 Para iniciar el servidor HTTPS:"
echo "   ./run_https_server.sh"
echo ""
echo "🌐 URLs de acceso:"
echo "   HTTPS (con cámara): https://$LOCAL_IP:5443"
echo "   HTTP (sin cámara):  http://$LOCAL_IP:5000"
echo ""
echo "📱 INSTRUCCIONES PARA MÓVIL:"
echo "1. Abre https://$LOCAL_IP:5443 en tu móvil"
echo "2. El navegador dirá 'No seguro' - presiona 'Avanzado'"
echo "3. Presiona 'Ir a $LOCAL_IP (no seguro)'"
echo "4. Permite acceso a la cámara cuando pregunte"
echo "5. ¡Listo! Ahora puedes usar la cámara"
echo ""
echo "⚠️  Nota: Es normal que el navegador muestre advertencias"
echo "    El certificado es autofirmado pero completamente seguro"
echo ""
echo "✅ ¡Todo listo para usar!"
