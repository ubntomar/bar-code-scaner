# 📸 Sistema de Códigos con Imágenes Asociadas

## 🎯 Nueva Funcionalidad

El Scanner Server ahora incluye un **sistema automático de captura y gestión de imágenes** asociadas a códigos de barras, perfecto para gestión de paquetes e inventario.

### ✨ Características Principales

- **📱 Captura Automática**: Conteo regresivo de 2 segundos tras escaneo exitoso
- **🔍 Búsqueda Instantánea**: Encuentra imágenes por código desde cualquier PC
- **💾 Base de Datos SQLite**: Almacenamiento local seguro y eficiente
- **🔄 Sobrescritura Inteligente**: Actualiza automáticamente imágenes duplicadas
- **📊 Estadísticas en Tiempo Real**: Monitoreo del sistema
- **🌐 Acceso Simultáneo**: Múltiples usuarios pueden buscar al mismo tiempo

---

## 🚀 Instalación y Configuración

### 1. Inicializar Base de Datos

```bash
# Ejecutar script de inicialización
python3 init_database.py
```

### 2. Iniciar Servidor

```bash
# Iniciar servidor HTTPS con nueva funcionalidad
python3 server_https.py
```

### 3. Verificar URLs

- **Scanner Principal**: `https://tu-ip:5443/`
- **Búsqueda de Imágenes**: `https://tu-ip:5443/buscar`
- **API Status**: `https://tu-ip:5443/status`

---

## 📱 Flujo de Trabajo - Escaneo con Captura

### Para la Secretaria (Escaneando):

1. **Escanear Código**: Apuntar cámara y presionar "ESCANEAR"
2. **Escaneo Exitoso**: ✅ Código aparece en pantalla
3. **Conteo Regresivo**: 2 segundos automático con overlay visual
4. **Captura Automática**: 📸 Flash y sonido confirman captura
5. **Imagen Guardada**: Sistema guarda imagen asociada al código

### Características del Conteo:
- **Overlay visual**: Pantalla completa con conteo grande
- **Efectos visuales**: Pulso en marco de cámara
- **Flash de captura**: Efecto blanco simulando flash real
- **Sonido confirmación**: Beep tipo pistola lectora

---

## 🔍 Búsqueda de Imágenes

### Para el Personal de Búsqueda:

1. **Acceder a Búsqueda**: `https://tu-ip:5443/buscar`
2. **Ingresar Código**: Escribir en campo de búsqueda
3. **Sugerencias Automáticas**: Autocompletado mientras escribe
4. **Ver Imagen**: Imagen aparece instantáneamente
5. **Información Detallada**: Fecha, tamaño, dispositivo de origen

### Funciones de Búsqueda:
- ⚡ **Búsqueda instantánea** por código completo
- 💭 **Sugerencias automáticas** mientras escribe
- 🕒 **Códigos recientes** para acceso rápido
- 📋 **Copiar código** al portapapeles
- 🔄 **Actualización automática** cada 30 segundos

---

## 📊 Gestión y Estadísticas

### Panel de Estadísticas (`/buscar`):

- **Total de códigos** almacenados
- **Espacio utilizado** en MB
- **Último código** escaneado
- **Tamaño base de datos**
- **Códigos recientes** con timestamps

### Base de Datos:

- **Archivo**: `scanner_database.db`
- **Formato**: SQLite (compatible multiplataforma)
- **Campos**: código, imagen_blob, timestamp, tamaño_kb, dispositivo
- **Índices**: Optimizado para búsquedas rápidas

---

## 🔧 Configuración Técnica

### Calidad de Imagen:
- **Resolución**: Media (optimizada para espacio)
- **Formato**: JPEG
- **Compresión**: 70% (balance calidad/tamaño)
- **Promedio**: ~100-300 KB por imagen

### Base de Datos:
```sql
CREATE TABLE codigos_imagenes (
    codigo TEXT PRIMARY KEY,
    imagen_blob BLOB NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tamaño_kb INTEGER,
    dispositivo TEXT
);
```

### APIs Disponibles:
- `POST /guardar-imagen` - Guardar imagen + código
- `GET /api/buscar/<codigo>` - Buscar imagen por código
- `GET /api/estadisticas` - Estadísticas del sistema
- `GET /api/recientes` - Códigos recientes
- `GET /api/buscar-coincidencias/<term>` - Autocompletado

---

## 🎛️ Configuración Avanzada

### Ajustar Tiempo de Conteo:
En `scanner.html`, línea ~890:
```javascript
let countdown = 2; // Cambiar por 3, 4, etc.
```

### Ajustar Calidad de Imagen:
En `scanner.html`, función `captureAndSaveImage`:
```javascript
const imageData = canvas.toDataURL('image/jpeg', 0.7); // 0.7 = 70% calidad
```

### Limpiar Imágenes Antiguas:
```python
# En Python console
from database import ImageDatabase
db = ImageDatabase()
db.cleanup_old_images(days_old=30)  # Eliminar >30 días
```

---

## 🔒 Seguridad y Acceso

### Red Local:
- ✅ **Sin autenticación** como solicitado
- ✅ **HTTPS obligatorio** para cámara móvil
- ✅ **Acceso simultáneo** desde múltiples PCs
- ✅ **Base de datos local** - no sale de la red

### Archivos Importantes:
- `scanner_database.db` - Base de datos principal
- `ssl_certs/` - Certificados HTTPS
- `database.py` - Módulo de base de datos
- `templates/buscar.html` - Interfaz de búsqueda

---

## 🚨 Solución de Problemas

### Base de Datos No Funciona:
```bash
# Verificar permisos
ls -la scanner_database.db
# Re-inicializar
python3 init_database.py
```

### Imágenes No Se Guardan:
1. Verificar consola del navegador (F12)
2. Verificar logs del servidor
3. Verificar espacio en disco
4. Verificar permisos de escritura

### Búsqueda No Funciona:
1. Verificar que el servidor esté corriendo
2. Acceder directamente a `/buscar`
3. Verificar API: `/api/estadisticas`

### Conteo No Aparece:
1. Verificar JavaScript habilitado
2. Comprobar que hay video activo
3. Verificar que el escaneo fue exitoso

---

## 📈 Casos de Uso

### ✅ Gestión de Paquetes:
- Secretaria escanea código del paquete
- Sistema captura imagen automáticamente
- Cliente muestra código a otra secretaria
- Segunda secretaria busca imagen instantáneamente
- Ubicación visual del paquete confirmada

### ✅ Control de Inventario:
- Escaneo + captura de productos
- Búsqueda visual por código
- Verificación de ubicación
- Historial de escaneado

### ✅ Entrega de Pedidos:
- Escaneo al recibir
- Búsqueda al entregar
- Confirmación visual
- Registro automático

---

## 🔧 Mantenimiento

### Respaldo de Base de Datos:
```bash
# Copiar archivo
cp scanner_database.db scanner_database_backup_$(date +%Y%m%d).db
```

### Estadísticas de Uso:
- Acceder a `/buscar` → "Ver Estadísticas"
- Monitorear tamaño de base de datos
- Revisar códigos más buscados

### Optimización:
- La base de datos se auto-optimiza
- Índices automáticos para búsquedas rápidas
- Compresión JPEG reduce espacio
- Sobrescritura automática evita duplicados

---

## 🎉 ¡Sistema Listo!

El Scanner Server ahora es un **sistema completo de gestión visual** que mantiene la **simplicidad tipo pistola lectora** mientras agrega **potentes capacidades de búsqueda por imagen**.

**🚀 Para comenzar**: Ejecuta `python3 init_database.py` seguido de `python3 server_https.py`