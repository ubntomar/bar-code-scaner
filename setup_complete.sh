#!/bin/bash

# Script de instalación completa para Scanner Server con Sistema de Imágenes
# Configura HTTPS + Base de Datos + Sistema de Códigos con Imágenes

set -e

echo "🎯 INSTALACIÓN COMPLETA - SCANNER SERVER CON IMÁGENES"
echo "======================================================="
echo "📱 Scanner tipo pistola lectora"
echo "📸 Captura automática de imágenes" 
echo "🔍 Sistema de búsqueda por código"
echo "💾 Base de datos SQLite local"
echo "======================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "server_https.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio scanner_server"
    echo "   cd scanner_server && ./setup_complete.sh"
    exit 1
fi

echo "📁 Directorio verificado: $(pwd)"

# Activar entorno virtual
if [ -d "venv" ]; then
    echo "🐍 Activando entorno virtual..."
    source venv/bin/activate
else
    echo "❌ Error: No se encontró entorno virtual."
    echo "💡 Crear primero: python3 -m venv venv && source venv/bin/activate"
    exit 1
fi

echo "📦 Instalando dependencias completas..."

# Instalar todas las dependencias
pip install flask==2.3.3
pip install pyzbar==0.1.9
pip install pynput==1.7.6
pip install pillow==10.0.1
pip install requests==2.31.0
pip install cryptography>=3.4.8
pip install pyopenssl>=21.0.0

echo "✅ Dependencias Python instaladas"

# Verificar dependencias del sistema (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Verificando dependencias del sistema Linux..."
    
    # Verificar zbar
    if ! dpkg -l | grep -q libzbar0; then
        echo "📦 Instalando libzbar para códigos de barras..."
        sudo apt-get update
        sudo apt-get install -y libzbar0 libzbar-dev
    fi
    
    # Verificar xdotool para gestión de foco
    if ! command -v xdotool &> /dev/null; then
        echo "📦 Instalando xdotool para gestión de foco..."
        sudo apt-get install -y xdotool
    fi
    
    # Verificar OpenSSL
    if ! command -v openssl &> /dev/null; then
        echo "📦 Instalando OpenSSL..."
        sudo apt-get install -y openssl
    fi
    
    echo "✅ Dependencias del sistema verificadas"
fi

# Verificar archivos principales
echo "🔍 Verificando archivos del sistema..."

required_files=(
    "server_https.py"
    "scanner.py" 
    "keyboard_sim.py"
    "database.py"
    "templates/scanner.html"
    "templates/buscar.html"
    "static/style.css"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - FALTANTE"
        echo "⚠️  Archivo requerido faltante: $file"
    fi
done

# Crear directorio para certificados SSL
echo "🔒 Configurando certificados HTTPS..."
mkdir -p ssl_certs

# Detectar IP local
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    LOCAL_IP=$(ipconfig | grep "IPv4" | head -1 | awk '{print $NF}')
else
    LOCAL_IP="192.168.1.100"
fi

echo "🌐 IP local detectada: $LOCAL_IP"

# Crear certificado SSL si no existe
if [ ! -f "ssl_certs/server.crt" ] || [ ! -f "ssl_certs/server.key" ]; then
    echo "🔐 Creando certificados SSL..."
    
    # Crear configuración OpenSSL
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

    # Crear certificado
    openssl req -x509 -newkey rsa:4096 -keyout ssl_certs/server.key -out ssl_certs/server.crt \
    -days 365 -nodes -config ssl_certs/openssl.conf -extensions v3_req

    if [ $? -eq 0 ]; then
        echo "✅ Certificados SSL creados"
    else
        echo "❌ Error creando certificados SSL"
        exit 1
    fi
else
    echo "✅ Certificados SSL ya existen"
fi

# Inicializar base de datos
echo "💾 Inicializando base de datos..."
python3 init_database.py

if [ $? -eq 0 ]; then
    echo "✅ Base de datos inicializada correctamente"
else
    echo "❌ Error inicializando base de datos"
    exit 1
fi

# Verificar permisos de archivos
echo "🔧 Verificando permisos..."
chmod +x server_https.py
chmod +x init_database.py
chmod +x setup_complete.sh

if [ -f "run_https_server.sh" ]; then
    chmod +x run_https_server.sh
fi

# Crear script de inicio si no existe
if [ ! -f "run_https_server.sh" ]; then
    echo "📝 Creando script de inicio..."
    cat > run_https_server.sh << 'EOF'
#!/bin/bash
echo "🔒 Iniciando Scanner Server HTTPS con Sistema de Imágenes..."
source venv/bin/activate
python3 server_https.py
EOF
    chmod +x run_https_server.sh
fi

# Verificar que todo funcione
echo "🧪 Verificando instalación..."

# Test de importaciones Python
python3 -c "
try:
    from database import ImageDatabase
    from scanner import BarcodeScanner  
    from keyboard_sim import KeyboardSimulator
    import flask
    print('✅ Todas las importaciones funcionan')
except ImportError as e:
    print(f'❌ Error de importación: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Error en verificación de Python"
    exit 1
fi

echo ""
echo "🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE"
echo "======================================"
echo ""
echo "🚀 PARA INICIAR EL SERVIDOR:"
echo "   ./run_https_server.sh"
echo "   O: python3 server_https.py"
echo ""
echo "🌐 URLS DE ACCESO:"
echo "   📱 Scanner:      https://$LOCAL_IP:5443/"
echo "   🔍 Búsqueda:     https://$LOCAL_IP:5443/buscar"
echo "   📊 Estado:       https://$LOCAL_IP:5443/status"
echo ""
echo "📸 NUEVA FUNCIONALIDAD:"
echo "   ✅ Escaneo → Conteo 2s → Captura automática"
echo "   ✅ Búsqueda instantánea por código"  
echo "   ✅ Base de datos SQLite local"
echo "   ✅ Acceso simultáneo múltiples usuarios"
echo ""
echo "📱 PARA MÓVILES:"
echo "   1. Abrir: https://$LOCAL_IP:5443"
echo "   2. Aceptar certificado 'no seguro'"
echo "   3. Permitir acceso a cámara"
echo "   4. ¡Comenzar a escanear!"
echo ""
echo "🔍 PARA BÚSQUEDA:"
echo "   1. Abrir: https://$LOCAL_IP:5443/buscar"
echo "   2. Escribir código en búsqueda"
echo "   3. Ver imagen asociada instantáneamente"
echo ""
echo "📋 ARCHIVOS IMPORTANTES:"
echo "   📄 database.py           - Módulo de base de datos"
echo "   📄 scanner_database.db   - Base de datos SQLite"
echo "   📁 ssl_certs/           - Certificados HTTPS"
echo "   📄 README_IMAGENES.md    - Documentación completa"
echo ""
echo "⚡ ¡SISTEMA LISTO PARA PRODUCCIÓN!"
echo "======================================"