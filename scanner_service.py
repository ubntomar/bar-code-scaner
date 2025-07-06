#!/usr/bin/env python3
"""
Script para instalar el servidor como servicio de Windows
Requiere: pip install pywin32
"""

import sys
import os
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil
import subprocess

class ScannerServerService(win32serviceutil.ServiceFramework):
    """Servicio de Windows para el Scanner Server"""
    
    _svc_name_ = "ScannerServerService"
    _svc_display_name_ = "Scanner Server - Códigos de Barras"
    _svc_description_ = "Servidor web para escaneo de códigos de barras con captura de imágenes"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        """Detener el servicio"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.process:
            self.process.terminate()

    def SvcDoRun(self):
        """Ejecutar el servicio"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Cambiar al directorio del proyecto
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Ejecutar el servidor
        python_exe = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')
        server_script = os.path.join(project_dir, 'server_https.py')
        
        try:
            self.process = subprocess.Popen([python_exe, server_script])
            
            # Esperar hasta que se detenga el servicio
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Error ejecutando servidor: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ScannerServerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ScannerServerService)
