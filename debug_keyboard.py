#!/usr/bin/env python3
"""
Debug específico para problema de escritura
Identifica exactamente por qué no aparece el texto
"""

import os
import subprocess
import time
import sys
from pynput.keyboard import Key, Controller

def check_session_type():
    """Verificar tipo de sesión gráfica"""
    print("🔍 VERIFICANDO SESIÓN GRÁFICA")
    print("=" * 40)
    
    # Verificar Wayland
    wayland = os.environ.get('WAYLAND_DISPLAY')
    xdg_session = os.environ.get('XDG_SESSION_TYPE')
    
    print(f"WAYLAND_DISPLAY: {wayland or 'No definido'}")
    print(f"XDG_SESSION_TYPE: {xdg_session or 'No definido'}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'No definido')}")
    
    if xdg_session == 'wayland' or wayland:
        print("⚠️  PROBLEMA DETECTADO: Sesión Wayland")
        print("   Wayland interfiere con pynput")
        print("   SOLUCIÓN: Cambiar a sesión X11")
        return False
    else:
        print("✅ Sesión X11 - Compatible")
        return True

def test_focus_methods():
    """Probar diferentes métodos de enfoque"""
    print("\n🎯 PROBANDO MÉTODOS DE ENFOQUE")
    print("=" * 40)
    
    keyboard = Controller()
    
    # Método 1: xdotool windowfocus
    try:
        print("🔧 Probando xdotool windowfocus...")
        result = subprocess.run(['xdotool', 'getwindowfocus'], capture_output=True, text=True)
        window_id = result.stdout.strip()
        print(f"   Ventana activa ID: {window_id}")
        
        # Forzar foco
        subprocess.run(['xdotool', 'windowfocus', window_id])
        print("   ✅ Foco forzado con xdotool")
        
    except Exception as e:
        print(f"   ❌ Error con xdotool: {e}")
    
    # Método 2: Simular click para asegurar foco
    try:
        print("🔧 Probando click para foco...")
        subprocess.run(['xdotool', 'getmouselocation'], check=True)
        # Un pequeño movimiento del mouse para activar ventana
        subprocess.run(['xdotool', 'mousemove_relative', '0', '0'])
        print("   ✅ Mouse activado")
        
    except Exception as e:
        print(f"   ❌ Error con mouse: {e}")

def test_different_apps():
    """Test con diferentes aplicaciones"""
    print("\n📝 PROBANDO DIFERENTES EDITORES")
    print("=" * 40)
    
    apps_to_test = [
        ('gedit', 'gedit'),
        ('terminal', 'gnome-terminal'),
        ('nano en terminal', 'gnome-terminal -- nano /tmp/test.txt'),
        ('mousepad', 'mousepad'),
        ('leafpad', 'leafpad')
    ]
    
    for app_name, command in apps_to_test:
        try:
            print(f"\n🚀 Probando {app_name}...")
            print(f"   Ejecutando: {command}")
            
            # Abrir aplicación
            process = subprocess.Popen(command.split(), 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            print(f"   ✅ {app_name} iniciado (PID: {process.pid})")
            time.sleep(2)  # Esperar que se abra
            
            # Intentar escribir
            keyboard = Controller()
            test_text = f"TEST {app_name.upper()} 123"
            
            # Forzar foco con xdotool
            try:
                subprocess.run(['xdotool', 'search', '--name', app_name.split()[0], 'windowfocus'], 
                             timeout=2, capture_output=True)
            except:
                pass
            
            print(f"   ✍️  Escribiendo: {test_text}")
            for char in test_text:
                keyboard.type(char)
                time.sleep(0.05)
            
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            
            # Preguntar al usuario
            response = input(f"   ❓ ¿Apareció '{test_text}' en {app_name}? (s/n): ").lower()
            
            if response in ['s', 'si', 'y', 'yes']:
                print(f"   ✅ ¡FUNCIONA con {app_name}!")
                return app_name
            else:
                print(f"   ❌ No funciona con {app_name}")
            
            # Cerrar aplicación
            try:
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
            except:
                pass
                
        except Exception as e:
            print(f"   ❌ Error probando {app_name}: {e}")
    
    return None

def test_timing_delays():
    """Probar diferentes delays"""
    print("\n⏱️  PROBANDO DIFERENTES DELAYS")
    print("=" * 40)
    
    print("Abre un editor de texto y posiciona el cursor...")
    input("Presiona Enter cuando estés listo...")
    
    keyboard = Controller()
    delays = [0.5, 1.0, 2.0, 5.0]
    
    for delay in delays:
        print(f"\n🔧 Probando delay de {delay} segundos...")
        print(f"   Cambiando al editor en {delay} segundos...")
        
        time.sleep(delay)
        
        test_text = f"DELAY-{delay}s"
        print(f"   ✍️  Escribiendo: {test_text}")
        
        for char in test_text:
            keyboard.type(char)
            time.sleep(0.05)
        
        keyboard.press(Key.space)
        keyboard.release(Key.space)
        
        response = input(f"   ❓ ¿Apareció con delay {delay}s? (s/n): ").lower()
        
        if response in ['s', 'si', 'y', 'yes']:
            print(f"   ✅ ¡Delay {delay}s funciona!")
            return delay
    
    return None

def test_alternative_methods():
    """Probar métodos alternativos"""
    print("\n🔄 PROBANDO MÉTODOS ALTERNATIVOS")
    print("=" * 40)
    
    # Método 1: xdotool type
    print("🔧 Probando xdotool type...")
    try:
        print("   Abre un editor y presiona Enter cuando estés listo...")
        input("   Presiona Enter...")
        
        time.sleep(2)
        test_text = "XDOTOOL-TYPE-TEST-123"
        
        result = subprocess.run(['xdotool', 'type', test_text], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            response = input(f"   ❓ ¿Apareció '{test_text}'? (s/n): ").lower()
            if response in ['s', 'si', 'y', 'yes']:
                print("   ✅ ¡xdotool type FUNCIONA!")
                return 'xdotool'
        else:
            print(f"   ❌ Error xdotool: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Error con xdotool: {e}")
    
    # Método 2: Clipboard + Ctrl+V
    print("\n🔧 Probando portapapeles...")
    try:
        import pyperclip
        print("   ✅ pyperclip disponible")
        
        test_text = "CLIPBOARD-TEST-456"
        pyperclip.copy(test_text)
        
        print("   Abre un editor y presiona Enter...")
        input("   Presiona Enter...")
        
        time.sleep(1)
        
        # Simular Ctrl+V
        keyboard = Controller()
        keyboard.press(Key.ctrl)
        keyboard.press('v')
        time.sleep(0.01)
        keyboard.release('v')
        keyboard.release(Key.ctrl)
        
        response = input(f"   ❓ ¿Apareció '{test_text}'? (s/n): ").lower()
        if response in ['s', 'si', 'y', 'yes']:
            print("   ✅ ¡Portapapeles FUNCIONA!")
            return 'clipboard'
            
    except ImportError:
        print("   ❌ pyperclip no instalado")
        print("   Instalar con: pip install pyperclip")
    except Exception as e:
        print(f"   ❌ Error portapapeles: {e}")
    
    return None

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO ESPECÍFICO DEL PROBLEMA")
    print("=" * 50)
    print("El simulador reporta éxito pero no aparece texto")
    print("Vamos a encontrar exactamente qué está pasando...")
    
    # 1. Verificar sesión
    session_ok = check_session_type()
    
    if not session_ok:
        print("\n🚨 PROBLEMA PRINCIPAL: WAYLAND")
        print("=" * 40)
        print("SOLUCIÓN:")
        print("1. Cerrar sesión")
        print("2. En pantalla de login, hacer clic en ⚙️")
        print("3. Seleccionar 'Ubuntu en X11'")
        print("4. Iniciar sesión")
        print("5. Probar nuevamente")
        return
    
    # 2. Test de enfoque
    test_focus_methods()
    
    # 3. Test con diferentes apps
    working_app = test_different_apps()
    
    if working_app:
        print(f"\n✅ SOLUCIÓN ENCONTRADA: Usar {working_app}")
    else:
        print("\n❌ No funciona con editores comunes")
        
        # 4. Test de timing
        working_delay = test_timing_delays()
        
        if working_delay:
            print(f"\n✅ SOLUCIÓN: Aumentar delay a {working_delay}s")
        else:
            # 5. Métodos alternativos
            working_method = test_alternative_methods()
            
            if working_method:
                print(f"\n✅ SOLUCIÓN: Usar método {working_method}")
            else:
                print("\n❌ Ningún método funciona")
                print("Problema posible: Permisos del sistema")

if __name__ == "__main__":
    main()
