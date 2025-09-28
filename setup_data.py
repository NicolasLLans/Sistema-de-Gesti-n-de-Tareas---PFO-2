#!/usr/bin/env python3
"""
Script para generar datos de prueba en el sistema
Crea usuarios y datos de ejemplo para demostración
"""

import requests
import json
import time
import random

class DataSetup:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def check_server(self) -> bool:
        """Verifica si el servidor está disponible"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            return response.status_code == 200
        except:
            return False
    
    def create_demo_users(self):
        """Crea usuarios de demostración"""
        demo_users = [
            {"usuario": "admin", "contraseña": "admin123"},
            {"usuario": "user1", "contraseña": "user123"},
            {"usuario": "testuser", "contraseña": "test123"},
            {"usuario": "demo", "contraseña": "demo123"},
            {"usuario": "guest", "contraseña": "guest123"}
        ]
        
        print("👥 Creando usuarios de demostración...")
        print("-" * 40)
        
        created_users = []
        
        for user_data in demo_users:
            try:
                response = self.session.post(f"{self.base_url}/registro", json=user_data)
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"✅ Usuario '{user_data['usuario']}' creado exitosamente")
                    created_users.append(user_data['usuario'])
                elif response.status_code == 409:
                    print(f"⚠️  Usuario '{user_data['usuario']}' ya existe")
                else:
                    error = response.json().get('error', 'Error desconocido')
                    print(f"❌ Error creando '{user_data['usuario']}': {error}")
                    
            except Exception as e:
                print(f"❌ Error con '{user_data['usuario']}': {e}")
        
        print(f"\n📊 Resumen: {len(created_users)} usuarios creados")
        return created_users
    
    def test_user_logins(self, usernames):
        """Prueba el login de usuarios creados"""
        print("\n🔐 Probando login de usuarios...")
        print("-" * 35)
        
        test_cases = [
            {"usuario": "admin", "contraseña": "admin123"},
            {"usuario": "user1", "contraseña": "user123"},
            {"usuario": "demo", "contraseña": "demo123"}
        ]
        
        successful_logins = 0
        
        for user_data in test_cases:
            try:
                response = self.session.post(f"{self.base_url}/login", json=user_data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Login exitoso para '{user_data['usuario']}'")
                    successful_logins += 1
                    
                    # Probar acceso a tareas
                    tareas_response = self.session.get(f"{self.base_url}/tareas")
                    if tareas_response.status_code == 200:
                        print(f"   └─ Acceso a tareas: ✅")
                    else:
                        print(f"   └─ Acceso a tareas: ❌ (HTTP {tareas_response.status_code})")
                    
                    # Logout
                    self.session.post(f"{self.base_url}/logout")
                    
                else:
                    error = response.json().get('error', 'Error desconocido')
                    print(f"❌ Login fallido para '{user_data['usuario']}': {error}")
                    
            except Exception as e:
                print(f"❌ Error en login '{user_data['usuario']}': {e}")
        
        print(f"\n📊 Logins exitosos: {successful_logins}/{len(test_cases)}")
        return successful_logins
    
    def show_system_status(self):
        """Muestra el estado actual del sistema"""
        print("\n📊 ESTADO ACTUAL DEL SISTEMA")
        print("=" * 35)
        
        try:
            response = self.session.get(f"{self.base_url}/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"🟢 Estado: {data.get('status', 'Unknown')}")
                print(f"💾 Base de datos: {data.get('database', 'Unknown')}")
                print(f"👥 Usuarios registrados: {data.get('usuarios_registrados', 0)}")
                print(f"📋 Tareas totales: {data.get('tareas_totales', 0)}")
                print(f"📦 Versión: {data.get('version', 'Unknown')}")
                print(f"🕐 Timestamp: {data.get('timestamp', 'Unknown')}")
            else:
                print(f"❌ Error obteniendo estado: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def generate_demo_scenarios(self):
        """Genera escenarios de demostración completos"""
        print("\n🎭 GENERANDO ESCENARIOS DE DEMOSTRACIÓN")
        print("=" * 45)
        
        scenarios = [
            {
                "name": "Registro exitoso",
                "user": {"usuario": f"scenario_user_{int(time.time())}", "contraseña": "demo123"},
                "description": "Usuario nuevo se registra correctamente"
            },
            {
                "name": "Login después de registro",
                "user": {"usuario": "admin", "contraseña": "admin123"},
                "description": "Usuario existente inicia sesión"
            },
            {
                "name": "Acceso a tareas autenticado",
                "user": {"usuario": "admin", "contraseña": "admin123"},
                "description": "Usuario accede a página protegida"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[Escenario {i}] {scenario['name']}")
            print(f"Descripción: {scenario['description']}")
            print("-" * 30)
            
            if scenario['name'] == "Registro exitoso":
                response = self.session.post(f"{self.base_url}/registro", json=scenario['user'])
                if response.status_code == 201:
                    print("✅ Registro exitoso")
                else:
                    print(f"❌ Error en registro: {response.status_code}")
            
            elif scenario['name'] == "Login después de registro":
                response = self.session.post(f"{self.base_url}/login", json=scenario['user'])
                if response.status_code == 200:
                    print("✅ Login exitoso")
                else:
                    print(f"❌ Error en login: {response.status_code}")
            
            elif scenario['name'] == "Acceso a tareas autenticado":
                # Primero login
                login_response = self.session.post(f"{self.base_url}/login", json=scenario['user'])
                if login_response.status_code == 200:
                    # Luego acceder a tareas
                    tareas_response = self.session.get(f"{self.base_url}/tareas")
                    if tareas_response.status_code == 200:
                        print("✅ Acceso a tareas exitoso")
                    else:
                        print(f"❌ Error accediendo a tareas: {tareas_response.status_code}")
                else:
                    print(f"❌ Error en login previo: {login_response.status_code}")
            
            time.sleep(0.5)  # Pausa entre escenarios
    
    def create_documentation_examples(self):
        """Crea ejemplos para documentación"""
        print("\n📚 CREANDO EJEMPLOS PARA DOCUMENTACIÓN")
        print("=" * 45)
        
        examples = []
        
        # Ejemplo 1: Registro
        print("\n[Ejemplo 1] Registro de usuario")
        user_data = {"usuario": "doc_example", "contraseña": "example123"}
        
        try:
            response = self.session.post(f"{self.base_url}/registro", json=user_data)
            examples.append({
                "endpoint": "POST /registro",
                "request": user_data,
                "status_code": response.status_code,
                "response": response.json() if response.status_code in [200, 201, 400, 409] else {"error": "Error del servidor"}
            })
            print(f"✅ Respuesta: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Ejemplo 2: Login
        print("\n[Ejemplo 2] Login de usuario")
        try:
            response = self.session.post(f"{self.base_url}/login", json=user_data)
            examples.append({
                "endpoint": "POST /login",
                "request": user_data,
                "status_code": response.status_code,
                "response": response.json() if response.status_code in [200, 400, 401, 404] else {"error": "Error del servidor"}
            })
            print(f"✅ Respuesta: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Ejemplo 3: Acceso a tareas
        print("\n[Ejemplo 3] Acceso a tareas")
        try:
            response = self.session.get(f"{self.base_url}/tareas")
            examples.append({
                "endpoint": "GET /tareas",
                "request": "N/A (requiere sesión activa)",
                "status_code": response.status_code,
                "response": "HTML page" if response.status_code == 200 else response.json()
            })
            print(f"✅ Respuesta: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Guardar ejemplos en archivo JSON
        try:
            with open('api_examples.json', 'w', encoding='utf-8') as f:
                json.dump(examples, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Ejemplos guardados en 'api_examples.json'")
        except Exception as e:
            print(f"❌ Error guardando ejemplos: {e}")
        
        return examples
    
    def run_complete_setup(self):
        """Ejecuta el setup completo del sistema"""
        print("🚀 SETUP COMPLETO DEL SISTEMA DE GESTIÓN DE TAREAS")
        print("=" * 55)
        
        if not self.check_server():
            print("❌ El servidor no está disponible en http://localhost:5000")
            print("💡 Ejecuta primero: python servidor.py")
            return False
        
        print("✅ Servidor disponible y funcionando")
        
        # Paso 1: Crear usuarios demo
        created_users = self.create_demo_users()
        
        # Paso 2: Probar logins
        successful_logins = self.test_user_logins(created_users)
        
        # Paso 3: Generar escenarios
        self.generate_demo_scenarios()
        
        # Paso 4: Crear ejemplos de documentación
        examples = self.create_documentation_examples()
        
        # Paso 5: Mostrar estado final
        self.show_system_status()
        
        # Resumen final
        print("\n" + "=" * 55)
        print("🎉 SETUP COMPLETADO")
        print("=" * 55)
        print("✅ Sistema configurado y listo para usar")
        print("📊 Usuarios de demo creados y probados")
        print("🎭 Escenarios de demostración ejecutados")
        print("📚 Ejemplos de API documentados")
        
        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Ejecutar tests: python test_api.py")
        print("2. Probar cliente: python cliente.py")
        print("3. Navegar a: http://localhost:5000")
        
        return True

def main():
    """Función principal"""
    print("⚙️  Sistema de Gestión de Tareas - Setup de Datos")
    print("Este script configurará datos de prueba y ejemplos")
    print("=" * 55)
    
    setup = DataSetup()
    setup.run_complete_setup()

if __name__ == "__main__":
    main()