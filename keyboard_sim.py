#!/usr/bin/env python3
"""
Simulador de teclado multiplataforma - VERSIÓN CON GESTIÓN INTELIGENTE DE FOCO
Compatible con Ubuntu y Windows - Maneja permisos, configuración y foco de ventanas
"""

import time
import platform
import logging
import subprocess
import os
from pynput.keyboard import Key, Controller

class KeyboardSimulator:
    """Clase para simular entrada de teclado con gestión inteligente de foco"""
    
    def __init__(self):
        """Inicializar el simulador de teclado"""
        self.keyboard = Controller()
        self.ready = False
        self.system = platform.system()
        self.last_error = None
        
        # Configuración por defecto
        self.config = {
            'typing_speed': 0.05,    # Delay entre teclas (más lento)
            'word_delay': 0.1,       # Delay entre palabras
            'line_delay': 0.2,       # Delay entre líneas
            'before_type_delay': 2.0, # Delay antes de escribir
            'capitalize': False,     # Convertir a mayúsculas
            'add_prefix': '',        # Prefijo antes del código
            'add_suffix': '',        # Sufijo después del código
            'remember_window': True, # Recordar ventana activa
            'focus_delay': 0.8,      # Delay después de enfocar ventana
        }
        
        # Variables para gestión de foco
        self.remembered_window = None
        self.last_active_window = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Verificar permisos y configuración
        self._check_permissions()
        self._test_basic_functionality()
        
        self.logger.info(f"Simulador inicializado en {self.system} - Ready: {self.ready}")
    
    def _check_permissions(self):
        """Verificar permisos en Ubuntu"""
        if self.system == "Linux":
            try:
                # Verificar si tenemos permisos para X11
                display = os.environ.get('DISPLAY')
                if not display:
                    self.last_error = "No hay DISPLAY configurado"
                    self.logger.error(self.last_error)
                    return False
                
                # Verificar acceso a X11
                result = subprocess.run(['xset', 'q'], capture_output=True, text=True)
                if result.returncode != 0:
                    self.last_error = "No se puede acceder a X11"
                    self.logger.error(self.last_error)
                    return False
                
                self.logger.info("✅ Permisos X11 verificados")
                return True
                
            except Exception as e:
                self.last_error = f"Error verificando permisos: {str(e)}"
                self.logger.error(self.last_error)
                return False
        
        return True
    
    def _test_basic_functionality(self):
        """Test básico de funcionalidad"""
        try:
            # Test simple - intentar presionar y soltar una tecla invisible
            self.keyboard.press(Key.ctrl)
            time.sleep(0.01)
            self.keyboard.release(Key.ctrl)
            
            self.ready = True
            self.logger.info("✅ Test básico de teclado exitoso")
            
        except Exception as e:
            self.last_error = f"Error en test básico: {str(e)}"
            self.logger.error(self.last_error)
            self.ready = False
    
    def remember_active_window(self):
        """Recordar la ventana activa antes del escaneo"""
        if not self.config['remember_window']:
            return True
            
        if self.system == "Linux":
            try:
                # Obtener ID de ventana activa
                result = subprocess.run(['xdotool', 'getwindowfocus'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    window_id = result.stdout.strip()
                    
                    # Obtener nombre de la ventana para debug
                    try:
                        name_result = subprocess.run(['xdotool', 'getwindowname', window_id],
                                                   capture_output=True, text=True, timeout=1)
                        window_name = name_result.stdout.strip() if name_result.returncode == 0 else "Desconocida"
                    except:
                        window_name = "Desconocida"
                    
                    self.remembered_window = window_id
                    self.logger.info(f"🎯 Ventana activa recordada: {window_name} (ID: {window_id})")
                    return True
                else:
                    self.logger.warning(f"No se pudo obtener ventana activa: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("Timeout obteniendo ventana activa")
                return False
            except Exception as e:
                self.logger.warning(f"Error recordando ventana: {e}")
                return False
        
        # En Windows o sin xdotool, no podemos hacer nada
        return True
    
    def focus_remembered_window(self):
        """Enfocar la ventana que estaba activa antes del escaneo"""
        if not self.config['remember_window'] or not self.remembered_window:
            return True
            
        if self.system == "Linux":
            try:
                # Verificar que la ventana aún existe
                check_result = subprocess.run(['xdotool', 'getwindowname', self.remembered_window],
                                            capture_output=True, text=True, timeout=2)
                
                if check_result.returncode != 0:
                    self.logger.warning("La ventana recordada ya no existe")
                    return False
                
                # Enfocar la ventana recordada
                focus_result = subprocess.run(['xdotool', 'windowfocus', self.remembered_window],
                                            capture_output=True, text=True, timeout=2)
                
                if focus_result.returncode == 0:
                    window_name = check_result.stdout.strip()
                    self.logger.info(f"✅ Foco restaurado a: {window_name}")
                    
                    # Esperar que la ventana se active completamente
                    time.sleep(self.config['focus_delay'])
                    
                    # Verificar que efectivamente está activa
                    verify_result = subprocess.run(['xdotool', 'getwindowfocus'],
                                                 capture_output=True, text=True, timeout=1)
                    if verify_result.returncode == 0:
                        current_window = verify_result.stdout.strip()
                        if current_window == self.remembered_window:
                            self.logger.info("🎯 Foco verificado correctamente")
                            return True
                        else:
                            self.logger.warning("El foco no se estableció correctamente")
                            return False
                    
                    return True
                else:
                    self.logger.warning(f"Error enfocando ventana: {focus_result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                self.logger.warning("Timeout enfocando ventana")
                return False
            except Exception as e:
                self.logger.warning(f"Error enfocando ventana recordada: {e}")
                return False
        
        return True
    
    def get_current_window_info(self):
        """Obtener información de la ventana actualmente activa"""
        if self.system == "Linux":
            try:
                # ID de ventana
                id_result = subprocess.run(['xdotool', 'getwindowfocus'],
                                         capture_output=True, text=True, timeout=1)
                if id_result.returncode != 0:
                    return None
                
                window_id = id_result.stdout.strip()
                
                # Nombre de ventana
                name_result = subprocess.run(['xdotool', 'getwindowname', window_id],
                                           capture_output=True, text=True, timeout=1)
                window_name = name_result.stdout.strip() if name_result.returncode == 0 else "Desconocida"
                
                # Clase de ventana
                class_result = subprocess.run(['xdotool', 'getwindowclassname', window_id],
                                            capture_output=True, text=True, timeout=1)
                window_class = class_result.stdout.strip() if class_result.returncode == 0 else "Desconocida"
                
                return {
                    'id': window_id,
                    'name': window_name,
                    'class': window_class
                }
                
            except Exception as e:
                self.logger.debug(f"Error obteniendo info de ventana: {e}")
                return None
        
        return None
    
    def is_ready(self):
        """Verificar si el simulador está listo"""
        return self.ready
    
    def get_last_error(self):
        """Obtener último error"""
        return self.last_error
    
    def type_text(self, text, focus_delay=None, restore_focus=True):
        """Escribir texto simulando teclado con gestión inteligente de foco"""
        if not self.ready:
            self.logger.error(f"Simulador no está listo: {self.last_error}")
            return False
        
        try:
            if not text:
                self.logger.warning("Texto vacío, no se escribirá nada")
                return False
            
            # Log del estado inicial
            current_window = self.get_current_window_info()
            if current_window:
                self.logger.info(f"Ventana actual antes de escribir: {current_window['name']}")
            
            # Restaurar foco a la ventana recordada si se solicita
            if restore_focus and self.remembered_window:
                focus_success = self.focus_remembered_window()
                if not focus_success:
                    self.logger.warning("No se pudo restaurar el foco, escribiendo en ventana actual")
            
            # Delay antes de escribir (si no se restauró foco o como tiempo adicional)
            delay = focus_delay if focus_delay is not None else self.config['before_type_delay']
            if not restore_focus or not self.remembered_window:
                self.logger.info(f"Esperando {delay} segundos para cambiar foco manualmente...")
                time.sleep(delay)
            
            # Aplicar transformaciones de configuración
            final_text = self.config['add_prefix'] + text + self.config['add_suffix']
            
            if self.config['capitalize']:
                final_text = final_text.upper()
            
            self.logger.info(f"Escribiendo: '{final_text}'")
            
            # Verificar ventana final antes de escribir
            final_window = self.get_current_window_info()
            if final_window:
                self.logger.info(f"Escribiendo en ventana: {final_window['name']}")
            
            # Escribir caracter por caracter
            success_count = 0
            for i, char in enumerate(final_text):
                try:
                    if char == ' ':
                        # Delay especial para espacios
                        self.keyboard.press(Key.space)
                        time.sleep(0.01)
                        self.keyboard.release(Key.space)
                        time.sleep(self.config['word_delay'])
                    elif char == '\n':
                        # Nueva línea
                        self.press_enter()
                        time.sleep(self.config['line_delay'])
                    else:
                        # Caracteres normales
                        self.keyboard.type(char)
                        time.sleep(self.config['typing_speed'])
                    
                    success_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error escribiendo caracter '{char}' en posición {i}: {e}")
                    continue
            
            success_rate = success_count / len(final_text)
            self.logger.info(f"Texto escrito - Éxito: {success_count}/{len(final_text)} ({success_rate:.1%})")
            
            return success_rate > 0.8  # Considerar exitoso si >80% de caracteres se escribieron
            
        except Exception as e:
            self.last_error = f"Error escribiendo texto: {str(e)}"
            self.logger.error(self.last_error)
            return False
    
    def type_text_alternative(self, text):
        """Método alternativo usando xdotool (solo Linux)"""
        if self.system != "Linux":
            return self.type_text(text)
        
        try:
            # Verificar si xdotool está disponible
            result = subprocess.run(['which', 'xdotool'], capture_output=True)
            if result.returncode != 0:
                self.logger.warning("xdotool no disponible, usando método normal")
                return self.type_text(text)
            
            # Aplicar transformaciones
            final_text = self.config['add_prefix'] + text + self.config['add_suffix']
            if self.config['capitalize']:
                final_text = final_text.upper()
            
            self.logger.info(f"Escribiendo con xdotool: '{final_text}'")
            
            # Esperar para cambio de foco
            time.sleep(self.config['before_type_delay'])
            
            # Usar xdotool para escribir
            result = subprocess.run(['xdotool', 'type', final_text], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info("✅ Texto escrito con xdotool")
                return True
            else:
                self.logger.error(f"Error con xdotool: {result.stderr}")
                return self.type_text(text)  # Fallback
                
        except Exception as e:
            self.logger.error(f"Error con xdotool: {e}")
            return self.type_text(text)  # Fallback
    
    def press_enter(self):
        """Presionar Enter"""
        try:
            self.keyboard.press(Key.enter)
            time.sleep(0.01)
            self.keyboard.release(Key.enter)
            self.logger.debug("Enter presionado")
            return True
        except Exception as e:
            self.logger.error(f"Error presionando Enter: {str(e)}")
            return False
    
    def press_tab(self):
        """Presionar Tab"""
        try:
            self.keyboard.press(Key.tab)
            time.sleep(0.01)
            self.keyboard.release(Key.tab)
            self.logger.debug("Tab presionado")
            return True
        except Exception as e:
            self.logger.error(f"Error presionando Tab: {str(e)}")
            return False
    
    def clear_input(self):
        """Limpiar entrada actual (Ctrl+A + Delete)"""
        try:
            # Seleccionar todo
            self.keyboard.press(Key.ctrl)
            self.keyboard.press('a')
            time.sleep(0.01)
            self.keyboard.release('a')
            self.keyboard.release(Key.ctrl)
            
            time.sleep(0.05)
            
            # Borrar
            self.keyboard.press(Key.delete)
            time.sleep(0.01)
            self.keyboard.release(Key.delete)
            
            self.logger.debug("Campo de entrada limpiado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error limpiando entrada: {str(e)}")
            return False
    
    def focus_test(self):
        """Test para verificar foco de ventana"""
        try:
            self.logger.info("=== TEST DE FOCO ===")
            self.logger.info("Cambia a un editor de texto en 3 segundos...")
            
            for i in range(3, 0, -1):
                self.logger.info(f"⏱️  {i}...")
                time.sleep(1)
            
            test_text = "TEST SCANNER 123"
            self.logger.info(f"Escribiendo: {test_text}")
            
            # Escribir sin delay
            return self.type_text(test_text, focus_delay=0)
            
        except Exception as e:
            self.logger.error(f"Error en test de foco: {e}")
            return False
    
    def install_dependencies_instructions(self):
        """Mostrar instrucciones para instalar dependencias"""
        if self.system == "Linux":
            print("\n" + "="*50)
            print("🔧 CONFIGURACIÓN ADICIONAL PARA UBUNTU")
            print("="*50)
            print("""
Para mejorar la compatibilidad, instala xdotool:

    sudo apt-get install xdotool

Para verificar permisos:

    echo $DISPLAY
    xset q

Si tienes problemas, intenta:

    1. Ejecutar desde terminal gráfico (no SSH)
    2. Asegurar que estás en sesión X11 (no Wayland)
    3. Verificar que no hay aplicaciones que bloqueen entrada
            """)
            print("="*50)
    
    def update_config(self, new_config):
        """Actualizar configuración del simulador"""
        old_config = self.config.copy()
        self.config.update(new_config)
        
        # Log de cambios importantes
        if 'before_type_delay' in new_config:
            self.logger.info(f"Delay antes de escribir cambiado: {old_config.get('before_type_delay')} → {self.config['before_type_delay']}")
        
        self.logger.info("Configuración de teclado actualizada")
    
    def get_config(self):
        """Obtener configuración actual"""
        return self.config
    
    def get_status(self):
        """Obtener estado completo del simulador"""
        current_window = self.get_current_window_info()
        
        return {
            'ready': self.ready,
            'system': self.system,
            'last_error': self.last_error,
            'config': self.config,
            'display': os.environ.get('DISPLAY', 'N/A') if self.system == "Linux" else 'N/A',
            'remembered_window': self.remembered_window,
            'current_window': current_window,
            'focus_management': self.system == "Linux" and self.config['remember_window']
        }
    
    def scan_and_type_workflow(self, text):
        """Workflow completo: recordar ventana, escribir código y restaurar foco"""
        try:
            self.logger.info("🚀 Iniciando workflow completo de escaneo y escritura")
            
            # Paso 1: Recordar ventana activa actual
            remember_success = self.remember_active_window()
            if not remember_success:
                self.logger.warning("No se pudo recordar la ventana activa")
            
            # Paso 2: Escribir el texto con restauración automática de foco
            type_success = self.type_text(text, restore_focus=True)
            
            if type_success:
                self.logger.info("✅ Workflow completado exitosamente")
            else:
                self.logger.warning("⚠️ Workflow completado con errores")
            
            return type_success
            
        except Exception as e:
            self.logger.error(f"Error en workflow completo: {e}")
            return False