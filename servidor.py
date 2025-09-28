from flask import Flask, request, jsonify, render_template_string, session
import sqlite3
import bcrypt
import os
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_segura'  # Cambiar en producción

# Configuración de la base de datos
DB_NAME = 'tareas.db'

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contraseña_hash TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de tareas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            completada BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hashea una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verifica una contraseña contra su hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def require_login(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'error': 'Debe iniciar sesión primero'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Página de inicio"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Gestión de Tareas</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f4f4f4; padding: 20px; border-radius: 5px; }
            .endpoint { background: white; margin: 10px 0; padding: 15px; border-radius: 3px; }
            .method { color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .post { background: #4CAF50; }
            .get { background: #2196F3; }
            code { background: #f0f0f0; padding: 2px 5px; border-radius: 2px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Sistema de Gestión de Tareas - API REST</h1>
            <p>Bienvenido al sistema de gestión de tareas. Esta API permite registrar usuarios, iniciar sesión y gestionar tareas.</p>
            
            <h2>📋 Endpoints Disponibles</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/registro</strong>
                <p>Registra un nuevo usuario en el sistema.</p>
                <p><strong>Body:</strong> <code>{"usuario": "nombre", "contraseña": "1234"}</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/login</strong>
                <p>Inicia sesión con credenciales de usuario.</p>
                <p><strong>Body:</strong> <code>{"usuario": "nombre", "contraseña": "1234"}</code></p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/tareas</strong>
                <p>Muestra esta página de bienvenida (requiere autenticación).</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/logout</strong>
                <p>Cierra la sesión actual.</p>
            </div>
            
            <h2>🔧 Cómo usar</h2>
            <ol>
                <li>Registra un usuario usando <code>POST /registro</code></li>
                <li>Inicia sesión con <code>POST /login</code></li>
                <li>Accede a <code>GET /tareas</code> para ver esta página</li>
            </ol>
            
            <h2>💡 Estado del Sistema</h2>
            <p><strong>Base de datos:</strong> SQLite ({{ db_status }})</p>
            <p><strong>Usuarios registrados:</strong> {{ user_count }}</p>
            <p><strong>Servidor:</strong> Flask + bcrypt para hashing seguro</p>
        </div>
    </body>
    </html>
    """
    
    # Obtener estadísticas
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    user_count = cursor.fetchone()[0]
    conn.close()
    
    db_status = "Conectada ✅" if os.path.exists(DB_NAME) else "No encontrada ❌"
    
    return render_template_string(html_template, 
                                user_count=user_count, 
                                db_status=db_status)

@app.route('/registro', methods=['POST'])
def registro():
    """Registra un nuevo usuario"""
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({'error': 'Faltan campos obligatorios: usuario y contraseña'}), 400
        
        usuario = data['usuario'].strip()
        contraseña = data['contraseña']
        
        # Validaciones básicas
        if len(usuario) < 3:
            return jsonify({'error': 'El usuario debe tener al menos 3 caracteres'}), 400
        
        if len(contraseña) < 4:
            return jsonify({'error': 'La contraseña debe tener al menos 4 caracteres'}), 400
        
        # Hashear la contraseña
        contraseña_hash = hash_password(contraseña)
        
        # Guardar en la base de datos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, contraseña_hash) VALUES (?, ?)",
                (usuario, contraseña_hash)
            )
            conn.commit()
            
            return jsonify({
                'mensaje': 'Usuario registrado exitosamente',
                'usuario': usuario,
                'fecha_registro': datetime.datetime.now().isoformat()
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'El usuario ya existe'}), 409
        
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({'error': f'Error del servidor: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Inicia sesión de usuario"""
    try:
        data = request.get_json()
        
        if not data or 'usuario' not in data or 'contraseña' not in data:
            return jsonify({'error': 'Faltan credenciales'}), 400
        
        usuario = data['usuario'].strip()
        contraseña = data['contraseña']
        
        # Buscar usuario en la base de datos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, usuario, contraseña_hash FROM usuarios WHERE usuario = ?",
            (usuario,)
        )
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        user_id, db_usuario, contraseña_hash = user_data
        
        # Verificar contraseña
        if not verify_password(contraseña, contraseña_hash):
            return jsonify({'error': 'Contraseña incorrecta'}), 401
        
        # Crear sesión
        session['usuario_id'] = user_id
        session['usuario'] = db_usuario
        
        return jsonify({
            'mensaje': 'Inicio de sesión exitoso',
            'usuario': db_usuario,
            'sesion_iniciada': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error del servidor: {str(e)}'}), 500

@app.route('/tareas', methods=['GET'])
@require_login
def tareas():
    """Muestra página de bienvenida para usuarios autenticados"""
    usuario_actual = session.get('usuario', 'Usuario')
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mis Tareas - Sistema de Gestión</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f4f4f4; padding: 20px; border-radius: 5px; }
            .welcome { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .info-box { background: white; padding: 15px; margin: 10px 0; border-radius: 3px; border-left: 4px solid #4CAF50; }
            .logout-btn { background: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; display: inline-block; margin-top: 10px; }
            .stats { display: flex; gap: 20px; margin: 20px 0; }
            .stat-card { background: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="welcome">
                <h1>🎉 ¡Bienvenido {{ usuario }}!</h1>
                <p>Has iniciado sesión exitosamente en el Sistema de Gestión de Tareas.</p>
            </div>
            
            <div class="info-box">
                <h3>✅ Autenticación Exitosa</h3>
                <p>Tu sesión está activa y puedes acceder a todas las funcionalidades del sistema.</p>
                <p><strong>Usuario:</strong> {{ usuario }}</p>
                <p><strong>Sesión iniciada:</strong> {{ fecha_actual }}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>🔐 Seguridad</h3>
                    <p>Contraseña hasheada con bcrypt</p>
                </div>
                <div class="stat-card">
                    <h3>💾 Base de Datos</h3>
                    <p>SQLite persistente</p>
                </div>
                <div class="stat-card">
                    <h3>🚀 API REST</h3>
                    <p>Flask framework</p>
                </div>
            </div>
            
            <div class="info-box">
                <h3>🔧 Funcionalidades Implementadas</h3>
                <ul>
                    <li>✅ Registro de usuarios con validación</li>
                    <li>✅ Autenticación segura con hashing</li>
                    <li>✅ Sesiones de usuario</li>
                    <li>✅ Base de datos SQLite</li>
                    <li>✅ API REST endpoints</li>
                    <li>✅ Páginas HTML responsivas</li>
                </ul>
            </div>
            
            <a href="/logout" class="logout-btn">🚪 Cerrar Sesión</a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(
        html_template, 
        usuario=usuario_actual,
        fecha_actual=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Cierra la sesión del usuario"""
    usuario = session.get('usuario', 'Usuario')
    session.clear()
    
    return jsonify({
        'mensaje': f'Sesión cerrada exitosamente para {usuario}',
        'fecha_logout': datetime.datetime.now().isoformat()
    }), 200

@app.route('/status')
def status():
    """Endpoint para verificar el estado del sistema"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Contar usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    user_count = cursor.fetchone()[0]
    
    # Contar tareas
    cursor.execute("SELECT COUNT(*) FROM tareas")
    task_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'status': 'OK',
        'database': 'SQLite conectada',
        'usuarios_registrados': user_count,
        'tareas_totales': task_count,
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0'
    })

if __name__ == '__main__':
    # Inicializar la base de datos
    init_db()
    print("🚀 Iniciando servidor Flask...")
    print("📄 Base de datos SQLite inicializada")
    print("🔐 Sistema de autenticación con bcrypt listo")
    print("🌐 Accede a: http://localhost:5000")
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)