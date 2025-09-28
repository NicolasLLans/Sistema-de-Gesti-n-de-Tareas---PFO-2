#!/usr/bin/env python3
"""
Script de instalación automática para el Sistema de Gestión de Tareas
Instala dependencias y configura el entorno de desarrollo
"""

import subprocess
import sys
import os
import platform
import venv

class ProjectInstaller:
    def __init__(self):
        self.project_name = "Sistema de Gestión de Tareas"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.os_info = platform.system()
        self.venv_name = "venv"
    
    def print_header(self):
        """Imprime el header del instalador"""
        print("=" * 60)
        print(f"🚀 INSTALADOR - {self.project_name}")
        print("=" * 60)
        print(f"🐍 Python: {self.python_version}")
        print(f"💻 Sistema: {self.os_info}")
        print(f"📁 Directorio: {os.getcwd()}")
        print("=" * 60)
    
    def check_python_version(self):
        """Verifica que la versión de Python sea compatible"""
        print("\n🔍 Verificando versión de Python...")
        
        if sys.version_info < (3, 7):
            print(f"❌ Python {self.python_version} no es compatible")
            print("💡 Se requiere Python 3.7 o superior")
            return False
        
        print(f"✅ Python {self.python_version} es compatible")
        return True
    
    def create_virtual_environment(self):
        """Crea un entorno virtual"""
        print(f"\n🏗️  Creando entorno virtual '{self.venv_name}'...")
        
        if os.path.exists(self.venv_name):
            print(f"⚠️  El entorno virtual '{self.venv_name}' ya existe")
            response = input("¿Deseas recrearlo? (y/n): ").lower().strip()
            
            if response == 'y':
                import shutil
                shutil.rmtree(self.venv_name)
                print(f"🗑️  Entorno anterior eliminado")
            else:
                print("📁 Usando entorno existente")
                return True
        
        try:
            venv.create(self.venv_name, with_pip=True)
            print(f"✅ Entorno virtual '{self.venv_name}' creado exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error creando entorno virtual: {e}")
            return False
    
    def get_pip_path(self):
        """Obtiene la ruta del pip del entorno virtual"""
        if self.os_info == "Windows":
            return os.path.join(self.venv_name, "Scripts", "pip")
        else:
            return os.path.join(self.venv_name, "bin", "pip")
    
    def get_python_path(self):
        """Obtiene la ruta del python del entorno virtual"""
        if self.os_info == "Windows":
            return os.path.join(self.venv_name, "Scripts", "python")
        else:
            return os.path.join(self.venv_name, "bin", "python")
    
    def install_requirements(self):
        """Instala las dependencias del proyecto"""
        print("\n📦 Instalando dependencias...")
        
        pip_path = self.get_pip_path()
        
        if not os.path.exists("requirements.txt"):
            print("❌ Archivo requirements.txt no encontrado")
            print("🔧 Creando requirements.txt básico...")
            
            basic_requirements = [
                "Flask==2.3.3",
                "bcrypt==4.0.1",
                "Werkzeug==2.3.7",
                "requests==2.31.0"
            ]
            
            with open("requirements.txt", "w") as f:
                f.write("\n".join(basic_requirements))
            
            print("✅ requirements.txt creado")
        
        try:
            # Actualizar pip
            subprocess.run([pip_path, "install", "--upgrade", "pip"], 
                         check=True, capture_output=True, text=True)
            print("✅ pip actualizado")
            
            # Instalar dependencias
            result = subprocess.run([pip_path, "install", "-r", "requirements.txt"], 
                                  check=True, capture_output=True, text=True)
            print("✅ Dependencias instaladas exitosamente")
            
            # Mostrar paquetes instalados
            result = subprocess.run([pip_path, "list"], 
                                  check=True, capture_output=True, text=True)
            
            installed_packages = [line for line in result.stdout.split('\n') 
                                if any(pkg in line.lower() for pkg in ['flask', 'bcrypt', 'werkzeug', 'requests'])]
            
            if installed_packages:
                print("\n📋 Paquetes principales instalados:")
                for package in installed_packages:
                    if package.strip():
                        print(f"   • {package.strip()}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando dependencias: {e}")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            return False
    
    def verify_installation(self):
        """Verifica que la instalación sea correcta"""
        print("\n🔍 Verificando instalación...")
        
        python_path = self.get_python_path()
        
        # Test imports
        test_script = '''
import sys
try:
    import flask
    print(f"✅ Flask {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask: {e}")

try:
    import bcrypt
    print("✅ bcrypt disponible")
except ImportError as e:
    print(f"❌ bcrypt: {e}")

try:
    import sqlite3
    print("✅ SQLite3 disponible")
except ImportError as e:
    print(f"❌ SQLite3: {e}")

try:
    import requests
    print(f"✅ Requests disponible")
except ImportError as e:
    print(f"❌ Requests: {e}")
'''
        
        try:
            result = subprocess.run([python_path, "-c", test_script], 
                                  check=True, capture_output=True, text=True)
            
            print("📦 Estado de dependencias:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en verificación: {e}")
            return False
    
    def create_run_scripts(self):
        """Crea scripts de ejecución convenientes"""
        print("\n📝 Creando scripts de ejecución...")
        
        python_path = self.get_python_path()
        
        if self.os_info == "Windows":
            # Script para Windows
            run_server_script = f'''@echo off
echo 🚀 Iniciando servidor Flask...
"{python_path}" servidor.py
pause
'''
            
            run_client_script = f'''@echo off
echo 📱 Iniciando cliente de consola...
"{python_path}" cliente.py
pause
'''
            
            run_tests_script = f'''@echo off
echo 🧪 Ejecutando tests...
"{python_path}" test_api.py
pause
'''
            
            with open("run_server.bat", "w") as f:
                f.write(run_server_script)
            
            with open("run_client.bat", "w") as f:
                f.write(run_client_script)
            
            with open("run_tests.bat", "w") as f:
                f.write(run_tests_script)
            
            print("✅ Scripts .bat creados para Windows")
            
        else:
            # Scripts para Unix/Linux/Mac
            run_server_script = f'''#!/bin/bash
echo "🚀 Iniciando servidor Flask..."
"{python_path}" servidor.py
'''
            
            run_client_script = f'''#!/bin/bash
echo "📱 Iniciando cliente de consola..."
"{python_path}" cliente.py
'''
            
            run_tests_script = f'''#!/bin/bash
echo "🧪 Ejecutando tests..."
"{python_path}" test_api.py
'''
            
            with open("run_server.sh", "w") as f:
                f.write(run_server_script)
            
            with open("run_client.sh", "w") as f:
                f.write(run_client_script)
            
            with open("run_tests.sh", "w") as f:
                f.write(run_tests_script)
            
            # Hacer ejecutables
            os.chmod("run_server.sh", 0o755)
            os.chmod("run_client.sh", 0o755)
            os.chmod("run_tests.sh", 0o755)
            
            print("✅ Scripts .sh creados para Unix/Linux/Mac")
    
    def show_activation_instructions(self):
        """Muestra instrucciones para activar el entorno virtual"""
        print("\n🔧 INSTRUCCIONES DE ACTIVACIÓN DEL ENTORNO VIRTUAL")
        print("-" * 55)
        
        if self.os_info == "Windows":
            print(f"Windows (CMD):     {self.venv_name}\\Scripts\\activate.bat")
            print(f"Windows (PowerShell): {self.venv_name}\\Scripts\\Activate.ps1")
        else:
            print(f"Unix/Linux/Mac:    source {self.venv_name}/bin/activate")
        
        print("\nPara desactivar:   deactivate")
    
    def show_usage_instructions(self):
        """Muestra instrucciones de uso del proyecto"""
        print("\n🚀 INSTRUCCIONES DE USO")
        print("=" * 30)
        print("1️⃣  Activar entorno virtual (ver instrucciones arriba)")
        print("2️⃣  Ejecutar servidor:")
        if self.os_info == "Windows":
            print("   • Doble clic en run_server.bat")
            print("   • O ejecutar: python servidor.py")
        else:
            print("   • Ejecutar: ./run_server.sh")
            print("   • O ejecutar: python servidor.py")
        
        print("3️⃣  Abrir navegador en: http://localhost:5000")
        print("4️⃣  Probar cliente de consola:")
        if self.os_info == "Windows":
            print("   • Doble clic en run_client.bat")
        else:
            print("   • Ejecutar: ./run_client.sh")
        
        print("5️⃣  Ejecutar tests automatizados:")
        if self.os_info == "Windows":
            print("   • Doble clic en run_tests.bat")
        else:
            print("   • Ejecutar: ./run_tests.sh")
    
    def install(self):
        """Ejecuta la instalación completa"""
        self.print_header()
        
        # Verificar Python
        if not self.check_python_version():
            return False
        
        # Crear entorno virtual
        if not self.create_virtual_environment():
            return False
        
        # Instalar dependencias
        if not self.install_requirements():
            return False
        
        # Verificar instalación
        if not self.verify_installation():
            return False
        
        # Crear scripts de ejecución
        self.create_run_scripts()
        
        # Mostrar instrucciones
        self.show_activation_instructions()
        self.show_usage_instructions()
        
        # Mensaje final
        print("\n" + "=" * 60)
        print("🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("✅ Entorno virtual configurado")
        print("✅ Dependencias instaladas")
        print("✅ Scripts de ejecución creados")
        print("✅ Proyecto listo para usar")
        
        return True

def main():
    """Función principal"""
    installer = ProjectInstaller()
    
    try:
        success = installer.install()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado durante la instalación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()