"""
Punto de entrada principal - Flask Application
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, redirect, url_for, session

# Verificar conexión a base de datos al inicio
print("\n" + "="*50)
print("FLOOR PLAN MANAGER - Iniciando...")
print("="*50)

try:
    from modules.db_module import test_connection, DB_CONFIG
    print(f"[DB] Conectando a {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}...")
    
    if test_connection():
        print("[DB] ✓ Conexión establecida correctamente")
    else:
        print("[DB] ✗ ERROR: No se pudo conectar a la base de datos")
        print("[DB] Verifica las credenciales en .env")
except Exception as e:
    print(f"[DB] ✗ ERROR: {e}")

print("="*50 + "\n")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Registrar blueprint API
from modules.api import api_bp
app.register_blueprint(api_bp)

@app.route('/')
def index():
    """Renderiza la aplicación principal."""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Página de login."""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)
