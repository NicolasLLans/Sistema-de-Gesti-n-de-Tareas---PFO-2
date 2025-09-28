#!/usr/bin/env python3
"""
Cliente de consola para el Sistema de Gestión de Tareas
Permite probar la API desde la línea de comandos
"""

import requests
import json
import sys
from typing import Optional

class ClienteTareas:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def mostrar_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*50)
        print("🚀 SISTEMA DE GESTIÓN DE TAREAS - CLIENTE")
        print("="*50)
        print("1. 📝 Registrar nuevo usuario")
        print("2. 🔐 Iniciar sesión")
        print("3. 📋 Ver página de tareas")
        print("4. 📊 Ver estado del sistema")
        print("5. 🚪 Cerrar sesión")
        print("6. ❌ Salir")
        print("="*50)
    
    def registrar_usuario(self):
        """Registra un nuevo usuario"""
        print("\n📝 REGISTRO DE USUARIO")
        print("-" * 30)
        
        usuario = input("Usuario (mín. 3 caracteres): ").strip()
        if len(usuario) < 3:
            print("❌ El usuario debe tener al menos 3 caracteres")
            return
        
        contraseña = input("Contraseña (mín. 4 caracteres): ").strip()
        if len(contraseña) < 4:
            print("❌ La contraseña debe tener al menos 4 caracteres")
            return
        
        data = {
            "usuario": usuario,
            "contraseña": contraseña
        }
        
        try:
            response = self.session.post(f"{self.base_url}/registro", json=data)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ {result['mensaje']}")
                print(f"👤 Usuario: {result['usuario']}")
                print(f"📅 Fecha: {result['fecha_registro']}")
            else:
                error = response.json().get('error', 'Error desconocido')
                print(f"❌ Error: {error}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al servidor. ¿Está ejecutándose?")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def iniciar_sesion(self):
        """Inicia sesión de usuario"""
        print("\n🔐 INICIO DE SESIÓN")
        print("-" * 25)
        
        usuario = input("Usuario: ").strip()
        contraseña = input("Contraseña: ").strip()
        
        data = {
            "usuario": usuario,
            "contraseña": contraseña
        }
        
        try:
            response = self.session.post(f"{self.base_url}/login", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['mensaje']}")
                print(f"👤 Usuario: {result['usuario']}")
                print(f"🕐 Sesión iniciada: {result['sesion_iniciada']}")
            else:
                error = response.json().get('error', 'Error desconocido')
                print(f"❌ Error: {error}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def ver_tareas(self):
        """Accede a la página de tareas"""
        print("\n📋 ACCEDIENDO A TAREAS...")
        
        try:
            response = self.session.get(f"{self.base_url}/tareas")
            
            if response.status_code == 200:
                print("✅ Acceso exitoso a la página de tareas")
                print("🌐 Abre tu navegador en: http://localhost:5000/tareas")
                print("📄 La página HTML está disponible para visualización")
            elif response.status_code == 401:
                error = response.json().get('error', 'No autenticado')
                print(f"❌ Error de autenticación: {error}")
                print("💡 Sugerencia: Inicia sesión primero")
            else:
                print(f"❌ Error HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def ver_estado(self):
        """Muestra el estado del sistema"""
        print("\n📊 ESTADO DEL SISTEMA")
        print("-" * 25)
        
        try:
            response = self.session.get(f"{self.base_url}/status")
            
            if response.status_code == 200:
                result = response.json()
                print(f"🟢 Estado: {result['status']}")
                print(f"💾 Base de datos: {result['database']}")
                print(f"👥 Usuarios registrados: {result['usuarios_registrados']}")
                print(f"📋 Tareas totales: {result['tareas_totales']}")
                print(f"🕐 Timestamp: {result['timestamp']}")
                print(f"📦 Versión: {result['version']}")
            else:
                print(f"❌ Error al obtener estado: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        print("\n🚪 CERRANDO SESIÓN...")
        
        try:
            response = self.session.post(f"{self.base_url}/logout")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['mensaje']}")
                print(f"🕐 Fecha logout: {result['fecha_logout']}")
            else:
                print("❌ Error al cerrar sesión")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al servidor")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def probar_servidor(self):
        """Verifica si el servidor está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            return response.status_code == 200
        except:
            return False
    
    def ejecutar(self):
        """Bucle principal del cliente"""
        print("🚀 Iniciando cliente de tareas...")
        
        # Verificar conexión al servidor
        if not self.probar_servidor():
            print("❌ No se puede conectar al servidor en http://localhost:5000")
            print("💡 Asegúrate de que el servidor esté ejecutándose:")
            print("   python servidor.py")
            sys.exit(1)
        
        print("✅ Conectado al servidor exitosamente")
        
        while True:
            try:
                self.mostrar_menu()
                opcion = input("\n👉 Selecciona una opción (1-6): ").strip()
                
                if opcion == '1':
                    self.registrar_usuario()
                elif opcion == '2':
                    self.iniciar_sesion()
                elif opcion == '3':
                    self.ver_tareas()
                elif opcion == '4':
                    self.ver_estado()
                elif opcion == '5':
                    self.cerrar_sesion()
                elif opcion == '6':
                    print("\n👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Selecciona 1-6.")
                
                input("\n⏸️  Presiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Saliendo del cliente...")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                input("⏸️  Presiona Enter para continuar...")

def main():
    """Función principal"""
    cliente = ClienteTareas()
    cliente.ejecutar()

if __name__ == "__main__":
    main()