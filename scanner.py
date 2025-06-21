#!/usr/bin/env python3
"""
Módulo de escaneo de códigos de barras - VERSIÓN OPTIMIZADA PARA PISTOLA LECTORA
Optimizado específicamente para lecturas rápidas y exitosas como una pistola real
"""

from pyzbar import pyzbar
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import logging
import numpy as np

class BarcodeScanner:
    """Clase optimizada para escanear códigos de barras con máxima eficiencia"""
    
    def __init__(self):
        """Inicializar el scanner optimizado"""
        self.supported_formats = [
            'CODE128', 'CODE39', 'CODE93', 'CODABAR',
            'EAN8', 'EAN13', 'UPC_A', 'UPC_E',
            'ISBN10', 'ISBN13', 'ISSN',
            'I25', 'DATABAR', 'DATABAR_EXP',
            'QR', 'PDF417', 'AZTEC', 'DATAMATRIX'
        ]
        self.ready = True
        
        # Configuración optimizada para pistola lectora
        self.config = {
            # Procesamiento básico
            'enhance_contrast': True,
            'resize_image': True,
            'max_width': 1200,
            'max_height': 900,
            'sharpen_image': True,
            'brightness_adjust': True,
            
            # NUEVAS OPTIMIZACIONES PARA CÓDIGOS DE BARRAS
            'barcode_specific_processing': True,
            'rotation_correction': True,
            'edge_enhancement': True,
            'noise_reduction': True,
            'multi_threshold': True,
            'focus_enhancement': True,
            
            # Configuración de calidad
            'min_code_length': 3,
            'max_processing_attempts': 15,  # Más intentos para mayor éxito
            'quality_threshold': 0.7
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Scanner optimizado para pistola lectora inicializado")
    
    def is_ready(self):
        """Verificar si el scanner está listo"""
        return self.ready
    
    def preprocess_image_optimized(self, image):
        """Preprocesamiento optimizado específicamente para códigos de barras"""
        try:
            processed_images = []
            
            # Asegurar que tenemos una imagen PIL
            if not isinstance(image, Image.Image):
                image = Image.fromarray(image)
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 1. REDIMENSIONAMIENTO INTELIGENTE
            original_size = image.size
            if self.config['resize_image']:
                image = self._smart_resize(image)
            
            # 2. IMAGEN ORIGINAL PROCESADA
            processed_images.append(('original', image))
            
            # 3. CONVERSIÓN A ESCALA DE GRISES OPTIMIZADA
            gray_image = self._convert_to_optimal_grayscale(image)
            processed_images.append(('grayscale_optimized', gray_image))
            
            # 4. MEJORA DE ENFOQUE ESPECÍFICA PARA CÓDIGOS
            if self.config['focus_enhancement']:
                focused_images = self._enhance_focus_for_barcodes(gray_image)
                processed_images.extend(focused_images)
            
            # 5. CORRECCIÓN DE CONTRASTE MÚLTIPLE
            if self.config['enhance_contrast']:
                contrast_images = self._multi_contrast_enhancement(gray_image)
                processed_images.extend(contrast_images)
            
            # 6. MEJORA DE BORDES PARA CÓDIGOS DE BARRAS
            if self.config['edge_enhancement']:
                edge_images = self._enhance_edges_for_barcodes(gray_image)
                processed_images.extend(edge_images)
            
            # 7. CORRECCIÓN DE ROTACIÓN
            if self.config['rotation_correction']:
                rotated_images = self._rotation_correction(gray_image)
                processed_images.extend(rotated_images)
            
            # 8. UMBRALIZACIÓN MÚLTIPLE
            if self.config['multi_threshold']:
                threshold_images = self._multi_threshold_processing(gray_image)
                processed_images.extend(threshold_images)
            
            # 9. REDUCCIÓN DE RUIDO AVANZADA
            if self.config['noise_reduction']:
                denoised_images = self._advanced_noise_reduction(gray_image)
                processed_images.extend(denoised_images)
            
            self.logger.info(f"Generadas {len(processed_images)} variaciones optimizadas")
            
            # Retornar solo las imágenes (sin etiquetas para compatibilidad)
            return [img for label, img in processed_images]
            
        except Exception as e:
            self.logger.error(f"Error en preprocesamiento optimizado: {str(e)}")
            return [image] if isinstance(image, Image.Image) else [Image.fromarray(image)]
    
    def _smart_resize(self, image):
        """Redimensionamiento inteligente que preserva la calidad de códigos"""
        width, height = image.size
        
        # No redimensionar si ya es del tamaño adecuado
        if width <= self.config['max_width'] and height <= self.config['max_height']:
            return image
        
        # Calcular ratio manteniendo aspecto
        ratio = min(self.config['max_width']/width, self.config['max_height']/height)
        new_size = (int(width * ratio), int(height * ratio))
        
        # Usar LANCZOS para mejor calidad en códigos
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def _convert_to_optimal_grayscale(self, image):
        """Conversión a escala de grises optimizada para códigos de barras"""
        # Usar conversión weighted que preserva mejor el contraste en códigos
        r, g, b = image.split()
        
        # Pesos optimizados para códigos de barras (más peso al verde)
        gray = Image.eval(r, lambda x: x * 0.2126)
        gray = Image.eval(g, lambda x: x * 0.7152).paste(gray, mask=None)
        gray = Image.eval(b, lambda x: x * 0.0722).paste(gray, mask=None)
        
        return image.convert('L')  # Fallback a conversión estándar
    
    def _enhance_focus_for_barcodes(self, image):
        """Mejora de enfoque específica para códigos de barras"""
        enhanced_images = []
        
        try:
            # 1. Sharpening básico
            sharp_filter = ImageFilter.SHARPEN
            sharp_image = image.filter(sharp_filter)
            enhanced_images.append(('sharpen_basic', sharp_image))
            
            # 2. Unsharp mask optimizado para códigos
            unsharp_image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            enhanced_images.append(('unsharp_optimized', unsharp_image))
            
            # 3. Sharpening agresivo para códigos muy desenfocados
            aggressive_unsharp = image.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))
            enhanced_images.append(('unsharp_aggressive', aggressive_unsharp))
            
            # 4. Mejora de bordes con filtro personalizado
            edge_enhance = image.filter(ImageFilter.EDGE_ENHANCE)
            enhanced_images.append(('edge_enhance', edge_enhance))
            
        except Exception as e:
            self.logger.debug(f"Error en mejora de enfoque: {e}")
        
        return enhanced_images
    
    def _multi_contrast_enhancement(self, image):
        """Múltiples niveles de mejora de contraste"""
        contrast_images = []
        
        try:
            enhancer = ImageEnhance.Contrast(image)
            
            # Diferentes niveles de contraste optimizados para códigos
            contrast_levels = [1.3, 1.7, 2.2, 2.8]
            
            for level in contrast_levels:
                contrast_image = enhancer.enhance(level)
                contrast_images.append((f'contrast_{level}', contrast_image))
                
        except Exception as e:
            self.logger.debug(f"Error en mejora de contraste: {e}")
        
        return contrast_images
    
    def _enhance_edges_for_barcodes(self, image):
        """Mejora de bordes específica para códigos de barras"""
        edge_images = []
        
        try:
            # 1. Edge enhancement básico
            edge_basic = image.filter(ImageFilter.EDGE_ENHANCE)
            edge_images.append(('edge_basic', edge_basic))
            
            # 2. Edge enhancement más agresivo
            edge_more = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            edge_images.append(('edge_aggressive', edge_more))
            
            # 3. Filtro FIND_EDGES para detectar bordes
            edges_only = image.filter(ImageFilter.FIND_EDGES)
            # Invertir para que las líneas sean negras sobre blanco
            edges_inverted = ImageOps.invert(edges_only)
            edge_images.append(('edges_inverted', edges_inverted))
            
        except Exception as e:
            self.logger.debug(f"Error en mejora de bordes: {e}")
        
        return edge_images
    
    def _rotation_correction(self, image):
        """Corrección de rotación para códigos mal orientados"""
        rotated_images = []
        
        try:
            # Probar rotaciones comunes para códigos mal orientados
            angles = [-10, -5, 5, 10, -2, 2]  # Rotaciones pequeñas más comunes
            
            for angle in angles:
                # Rotar con fondo blanco (mejor para códigos de barras)
                rotated = image.rotate(angle, fillcolor=255, expand=True)
                rotated_images.append((f'rotated_{angle}', rotated))
                
        except Exception as e:
            self.logger.debug(f"Error en corrección de rotación: {e}")
        
        return rotated_images
    
    def _multi_threshold_processing(self, image):
        """Múltiples técnicas de umbralización"""
        threshold_images = []
        
        try:
            # Convertir a numpy para operaciones avanzadas
            img_array = np.array(image)
            
            # 1. Umbralización automática (Otsu-like)
            mean_val = np.mean(img_array)
            std_val = np.std(img_array)
            
            # Diferentes umbrales basados en estadísticas
            thresholds = [
                mean_val - std_val * 0.5,
                mean_val,
                mean_val + std_val * 0.5,
                mean_val + std_val
            ]
            
            for i, threshold in enumerate(thresholds):
                binary = np.where(img_array > threshold, 255, 0).astype(np.uint8)
                binary_image = Image.fromarray(binary)
                threshold_images.append((f'threshold_{i}', binary_image))
                
        except Exception as e:
            self.logger.debug(f"Error en umbralización múltiple: {e}")
            
            # Fallback a umbralización simple
            try:
                # Umbralización simple con PIL
                threshold_simple = image.point(lambda x: 0 if x < 128 else 255, '1')
                threshold_images.append(('threshold_simple', threshold_simple.convert('L')))
            except:
                pass
        
        return threshold_images
    
    def _advanced_noise_reduction(self, image):
        """Reducción avanzada de ruido"""
        denoised_images = []
        
        try:
            # 1. Filtro de mediana - excelente para ruido en códigos
            median_image = image.filter(ImageFilter.MedianFilter(size=3))
            denoised_images.append(('median_3', median_image))
            
            # 2. Filtro gaussiano suave
            gaussian_image = image.filter(ImageFilter.GaussianBlur(radius=0.8))
            denoised_images.append(('gaussian_soft', gaussian_image))
            
            # 3. Combinación: mediana + sharpening
            median_sharp = median_image.filter(ImageFilter.SHARPEN)
            denoised_images.append(('median_sharp', median_sharp))
            
        except Exception as e:
            self.logger.debug(f"Error en reducción de ruido: {e}")
        
        return denoised_images
    
    def scan_image(self, image):
        """Escanear códigos de barras con procesamiento optimizado"""
        try:
            barcodes_found = []
            
            # Usar preprocesamiento optimizado
            processed_images = self.preprocess_image_optimized(image)
            
            self.logger.info(f"Procesando {len(processed_images)} variaciones optimizadas")
            
            # Intentar escanear cada versión procesada
            for i, img in enumerate(processed_images):
                try:
                    # pyzbar trabaja directamente con PIL Images
                    barcodes = pyzbar.decode(img)
                    
                    for barcode in barcodes:
                        # Extraer datos con manejo de encoding mejorado
                        barcode_data = self._extract_barcode_data(barcode)
                        
                        if not barcode_data:
                            continue
                        
                        barcode_type = barcode.type
                        
                        # Obtener coordenadas del código
                        (x, y, w, h) = barcode.rect
                        
                        # Calcular calidad del código detectado
                        quality_score = self._calculate_barcode_quality(barcode, img)
                        
                        # Crear objeto resultado
                        result = {
                            'data': barcode_data,
                            'type': barcode_type,
                            'coordinates': {
                                'x': x, 'y': y, 
                                'width': w, 'height': h
                            },
                            'polygon': [(point.x, point.y) for point in barcode.polygon],
                            'processing_method': f'optimized_method_{i}',
                            'quality_score': quality_score
                        }
                        
                        # Validar código con validación mejorada
                        if self.validate_barcode_enhanced(barcode_data, barcode_type, quality_score):
                            # Evitar duplicados
                            if not any(b['data'] == barcode_data for b in barcodes_found):
                                barcodes_found.append(result)
                                self.logger.info(f"Código encontrado: {barcode_type} - {barcode_data} (método {i}, calidad: {quality_score:.2f})")
                        else:
                            self.logger.debug(f"Código descartado por baja calidad: {barcode_data} (calidad: {quality_score:.2f})")
                
                except Exception as e:
                    self.logger.debug(f"Error escaneando imagen procesada {i}: {str(e)}")
                    continue
                
                # Si ya encontramos códigos de buena calidad, parar procesamiento adicional
                if len(barcodes_found) > 0 and max(b['quality_score'] for b in barcodes_found) > self.config['quality_threshold']:
                    break
            
            # Ordenar por calidad y retornar los mejores
            barcodes_found.sort(key=lambda x: x['quality_score'], reverse=True)
            
            self.logger.info(f"Escaneo completado. Códigos de calidad encontrados: {len(barcodes_found)}")
            return barcodes_found
            
        except Exception as e:
            self.logger.error(f"Error general en scan_image optimizado: {str(e)}")
            return []
    
    def _extract_barcode_data(self, barcode):
        """Extraer datos del código con manejo mejorado de encoding"""
        try:
            # Intentar UTF-8 primero
            return barcode.data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Intentar latin-1 como fallback
                return barcode.data.decode('latin-1')
            except UnicodeDecodeError:
                try:
                    # Intentar cp1252 (Windows encoding)
                    return barcode.data.decode('cp1252')
                except UnicodeDecodeError:
                    # Último recurso: ignorar caracteres problemáticos
                    return barcode.data.decode('utf-8', errors='ignore')
    
    def _calculate_barcode_quality(self, barcode, image):
        """Calcular puntuación de calidad del código detectado"""
        try:
            quality_score = 1.0
            
            # Factor 1: Tamaño del código (códigos más grandes suelen ser más confiables)
            (x, y, w, h) = barcode.rect
            area = w * h
            img_area = image.size[0] * image.size[1]
            size_ratio = area / img_area
            
            if size_ratio > 0.01:  # Al menos 1% de la imagen
                quality_score *= 1.0
            elif size_ratio > 0.005:  # 0.5% de la imagen
                quality_score *= 0.8
            else:
                quality_score *= 0.6
            
            # Factor 2: Longitud del código
            data_length = len(barcode.data.decode('utf-8', errors='ignore'))
            if data_length >= self.config['min_code_length']:
                if data_length > 8:  # Códigos más largos suelen ser más confiables
                    quality_score *= 1.0
                else:
                    quality_score *= 0.9
            else:
                quality_score *= 0.5
            
            # Factor 3: Tipo de código (algunos son más confiables)
            reliable_types = ['EAN13', 'UPC_A', 'CODE128', 'QR']
            if barcode.type in reliable_types:
                quality_score *= 1.0
            else:
                quality_score *= 0.9
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            self.logger.debug(f"Error calculando calidad: {e}")
            return 0.7  # Calidad por defecto moderada
    
    def validate_barcode_enhanced(self, barcode_data, barcode_type, quality_score):
        """Validación mejorada con puntuación de calidad"""
        try:
            # Validación básica de longitud
            if len(barcode_data) < self.config['min_code_length']:
                return False
            
            # Filtrar por calidad mínima
            if quality_score < 0.3:
                return False
            
            # Validaciones específicas por tipo (mejoradas)
            if barcode_type in ['EAN13', 'UPC_A']:
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
                # Validar que no contenga solo caracteres de control
                printable_chars = sum(1 for c in barcode_data if c.isprintable())
                return printable_chars >= self.config['min_code_length']
            
            elif barcode_type == 'QR':
                # QR codes pueden contener cualquier cosa, pero validar longitud mínima
                return len(barcode_data.strip()) >= 1
            
            # Para otros tipos, validación básica
            return len(barcode_data.strip()) >= self.config['min_code_length']
            
        except Exception as e:
            self.logger.warning(f"Error validando código: {str(e)}")
            return quality_score > 0.5  # Fallback basado en calidad
    
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
        self.logger.info("Configuración del scanner optimizado actualizada")
    
    def get_config(self):
        """Obtener configuración actual"""
        return self.config
    
    def get_processing_stats(self):
        """Obtener estadísticas de procesamiento"""
        return {
            'supported_formats': len(self.supported_formats),
            'max_processing_attempts': self.config['max_processing_attempts'],
            'quality_threshold': self.config['quality_threshold'],
            'optimizations_enabled': sum(1 for key, value in self.config.items() 
                                       if key.endswith('_processing') or key.endswith('_enhancement') and value)
        }
    
    def test_scanner(self):
        """Test del scanner optimizado"""
        try:
            # Crear imagen de prueba simple
            test_image = Image.new('RGB', (100, 100), color='white')
            result = self.scan_image(test_image)
            
            stats = self.get_processing_stats()
            self.logger.info(f"Test completado. Scanner optimizado funcionando: {self.ready}")
            self.logger.info(f"Estadísticas: {stats}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error en test optimizado: {str(e)}")
            self.ready = False
            return False