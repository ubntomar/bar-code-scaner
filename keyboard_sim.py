#!/usr/bin/env python3
"""
Simulador de teclado multiplataforma - VERSIÓN CORREGIDA
Compatible con Ubuntu y Windows - Maneja permisos y configuración
"""

import time
import platform
import logging
import subprocess
import os
from pynput.keyboard import Key, Controller

class KeyboardSimulator:
    """Clase para simular entrada de teclado"""
    
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
        }
        
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
    
    def is_ready(self):
        """Verificar si el simulador está listo"""
        return self.ready
    
    def get_last_error(self):
        """Obtener último error"""
        return self.last_error
    
    def type_text(self, text, focus_delay=None):
        """Escribir texto simulando teclado"""
        if not self.ready:
            self.logger.error(f"Simulador no está listo: {self.last_error}")
            return False
        
        try:
            if not text:
                self.logger.warning("Texto vacío, no se escribirá nada")
                return False
            
            # Delay antes de escribir para que el usuario pueda cambiar el foco
            delay = focus_delay if focus_delay is not None else self.config['before_type_delay']
            self.logger.info(f"Esperando {delay} segundos para cambiar foco...")
            time.sleep(delay)
            
            # Aplicar transformaciones de configuración
            final_text = self.config['add_prefix'] + text + self.config['add_suffix']
            
            if self.config['capitalize']:
                final_text = final_text.upper()
            
            self.logger.info(f"Escribiendo: '{final_text}'")
            
            # Intentar enfocar ventana activa primero
            try:
                if self.system == "Linux":
                    # Simular Alt+Tab para asegurar que hay una ventana activa
                    subprocess.run(['xdotool', 'key', 'alt+Tab'], 
                                 capture_output=True, timeout=1)
                    time.sleep(0.1)
            except:
                pass  # No es crítico si falla
            
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
        return {
            'ready': self.ready,
            'system': self.system,
            'last_error': self.last_error,
            'config': self.config,
            'display': os.environ.get('DISPLAY', 'N/A') if self.system == "Linux" else 'N/A'
        }
