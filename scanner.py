#!/usr/bin/env python3
"""
Módulo de escaneo de códigos de barras - VERSIÓN SIN OPENCV
Utiliza solo PIL y pyzbar para evitar conflictos con NumPy
"""

from pyzbar import pyzbar
from PIL import Image, ImageEnhance, ImageFilter
import logging

class BarcodeScanner:
    """Clase para escanear códigos de barras en imágenes usando solo PIL"""
    
    def __init__(self):
        """Inicializar el scanner"""
        self.supported_formats = [
            'CODE128', 'CODE39', 'CODE93', 'CODABAR',
            'EAN8', 'EAN13', 'UPC_A', 'UPC_E',
            'ISBN10', 'ISBN13', 'ISSN',
            'I25', 'DATABAR', 'DATABAR_EXP',
            'QR', 'PDF417', 'AZTEC', 'DATAMATRIX'
        ]
        self.ready = True
        
        # Configuración de procesamiento
        self.config = {
            'enhance_contrast': True,
            'resize_image': True,
            'max_width': 1200,
            'max_height': 900,
            'sharpen_image': True,
            'brightness_adjust': True
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Scanner inicializado sin OpenCV - usando solo PIL")
    
    def is_ready(self):
        """Verificar si el scanner está listo"""
        return self.ready
    
    def preprocess_image_pil(self, image):
        """Preprocesar imagen usando solo PIL"""
        try:
            processed_images = []
            
            # Asegurar que tenemos una imagen PIL
            if not isinstance(image, Image.Image):
                image = Image.fromarray(image)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionar si es muy grande
            if self.config['resize_image']:
                width, height = image.size
                if width > self.config['max_width'] or height > self.config['max_height']:
                    ratio = min(self.config['max_width']/width, self.config['max_height']/height)
                    new_size = (int(width * ratio), int(height * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Imagen original redimensionada
            processed_images.append(image)
            
            # Convertir a escala de grises
            gray_image = image.convert('L')
            processed_images.append(gray_image)
            
            # Mejorar contraste
            if self.config['enhance_contrast']:
                enhancer = ImageEnhance.Contrast(gray_image)
                contrast_image = enhancer.enhance(2.0)  # Aumentar contraste
                processed_images.append(contrast_image)
                
                # También una versión con menos contraste
                contrast_image_mild = enhancer.enhance(1.5)
                processed_images.append(contrast_image_mild)
            
            # Ajustar brillo
            if self.config['brightness_adjust']:
                enhancer = ImageEnhance.Brightness(gray_image)
                bright_image = enhancer.enhance(1.2)  # Más brillante
                processed_images.append(bright_image)
                
                dark_image = enhancer.enhance(0.8)   # Más oscuro
                processed_images.append(dark_image)
            
            # Aplicar sharpening
            if self.config['sharpen_image']:
                sharp_image = gray_image.filter(ImageFilter.SHARPEN)
                processed_images.append(sharp_image)
                
                # Sharpening más agresivo
                unsharp_image = gray_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                processed_images.append(unsharp_image)
            
            # Filtros adicionales
            # Filtro de mediana para reducir ruido
            median_image = gray_image.filter(ImageFilter.MedianFilter(size=3))
            processed_images.append(median_image)
            
            # Filtro Gaussiano
            blur_image = gray_image.filter(ImageFilter.GaussianBlur(radius=0.5))
            processed_images.append(blur_image)
            
            return processed_images
            
        except Exception as e:
            self.logger.error(f"Error en preprocesamiento PIL: {str(e)}")
            return [image] if isinstance(image, Image.Image) else [Image.fromarray(image)]
    
    def scan_image(self, image):
        """Escanear códigos de barras en una imagen usando solo PIL"""
        try:
            barcodes_found = []
            
            # Preprocesar imagen con diferentes técnicas
            processed_images = self.preprocess_image_pil(image)
            
            self.logger.info(f"Procesando {len(processed_images)} variaciones de la imagen")
            
            # Intentar escanear cada versión procesada
            for i, img in enumerate(processed_images):
                try:
                    # pyzbar trabaja directamente con PIL Images
                    barcodes = pyzbar.decode(img)
                    
                    for barcode in barcodes:
                        # Extraer datos
                        try:
                            barcode_data = barcode.data.decode('utf-8')
                        except UnicodeDecodeError:
                            # Si hay problemas de encoding, intentar con latin-1
                            barcode_data = barcode.data.decode('latin-1')
                        
                        barcode_type = barcode.type
                        
                        # Obtener coordenadas del código
                        (x, y, w, h) = barcode.rect
                        
                        # Crear objeto resultado
                        result = {
                            'data': barcode_data,
                            'type': barcode_type,
                            'coordinates': {
                                'x': x, 'y': y, 
                                'width': w, 'height': h
                            },
                            'polygon': [(point.x, point.y) for point in barcode.polygon],
                            'processing_method': f'method_{i}'
                        }
                        
                        # Validar código
                        if self.validate_barcode(barcode_data, barcode_type):
                            # Evitar duplicados
                            if not any(b['data'] == barcode_data for b in barcodes_found):
                                barcodes_found.append(result)
                                self.logger.info(f"Código encontrado: {barcode_type} - {barcode_data} (método {i})")
                        else:
                            self.logger.warning(f"Código inválido descartado: {barcode_data}")
                
                except Exception as e:
                    self.logger.debug(f"Error escaneando imagen procesada {i}: {str(e)}")
                    continue
                
                # Si ya encontramos códigos, no necesitamos procesar más imágenes
                if barcodes_found:
                    break
            
            self.logger.info(f"Escaneo completado. Códigos encontrados: {len(barcodes_found)}")
            return barcodes_found
            
        except Exception as e:
            self.logger.error(f"Error general en scan_image: {str(e)}")
            return []
    
    def validate_barcode(self, barcode_data, barcode_type):
        """Validar código de barras según su tipo"""
        try:
            # Validación básica de longitud
            if len(barcode_data) == 0:
                return False
            
            # Validaciones específicas por tipo
            if barcode_type in ['EAN13', 'UPC_A']:
                # EAN13/UPC-A deben ser numéricos y tener longitud correcta
                if not barcode_data.isdigit():
                    return False
                
                if barcode_type == 'EAN13' and len(barcode_data) != 13:
                    return False
                elif barcode_type == 'UPC_A' and len(barcode_data) not in [11, 12]:
                    return False
                
                # Validar checksum para EAN13
                if len(barcode_data) == 13:
                    return self.validate_ean13_checksum(barcode_data)
                
            elif barcode_type == 'EAN8':
                return len(barcode_data) == 8 and barcode_data.isdigit()
            
            elif barcode_type == 'UPC_E':
                return len(barcode_data) in [6, 8] and barcode_data.isdigit()
            
            elif barcode_type in ['CODE128', 'CODE39', 'CODE93']:
                # Códigos alfanuméricos - validación básica
                return len(barcode_data) >= 1
            
            elif barcode_type == 'QR':
                # QR codes pueden contener cualquier cosa
                return len(barcode_data) >= 1
            
            # Para otros tipos, aceptar si tienen contenido válido
            return len(barcode_data) >= 1
            
        except Exception as e:
            self.logger.warning(f"Error validando código: {str(e)}")
            return True  # En caso de error, aceptar el código
    
    def validate_ean13_checksum(self, barcode_data):
        """Validar checksum de código EAN13"""
        try:
            if len(barcode_data) != 13:
                return False
            
            # Calcular dígito de control
            digits = [int(d) for d in barcode_data[:-1]]
            checksum = 0
            
            for i, digit in enumerate(digits):
                if i % 2 == 0:
                    checksum += digit
                else:
                    checksum += digit * 3
            
            calculated_check = (10 - (checksum % 10)) % 10
            actual_check = int(barcode_data[-1])
            
            return calculated_check == actual_check
            
        except Exception as e:
            self.logger.warning(f"Error validando EAN13: {str(e)}")
            return True
    
    def get_supported_formats(self):
        """Obtener formatos soportados"""
        return self.supported_formats
    
    def update_config(self, new_config):
        """Actualizar configuración del scanner"""
        self.config.update(new_config)
        self.logger.info("Configuración del scanner actualizada")
    
    def get_config(self):
        """Obtener configuración actual"""
        return self.config
    
    def test_scanner(self):
        """Test del scanner con una imagen de prueba"""
        try:
            # Crear imagen de prueba simple
            test_image = Image.new('RGB', (100, 100), color='white')
            result = self.scan_image(test_image)
            self.logger.info(f"Test completado. Scanner funcionando: {self.ready}")
            return True
        except Exception as e:
            self.logger.error(f"Error en test: {str(e)}")
            self.ready = False
            return False
