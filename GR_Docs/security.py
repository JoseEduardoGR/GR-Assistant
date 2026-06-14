import os
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
from functools import wraps
from flask import request, jsonify

# Llave maestra para encriptar/desencriptar credenciales de clientes
# En producción, esto debería venir de variables de entorno seguras
SECRET_KEY = os.getenv("SAAS_SECRET_KEY", Fernet.generate_key().decode())
fernet = Fernet(SECRET_KEY.encode())

def get_db_connection():
    """Conecta a la base de datos PostgreSQL remota de SaaS."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database="grdocs_saas",
        user="postgres",
        # password=os.getenv("DB_PASSWORD", ""),
        cursor_factory=RealDictCursor
    )

def encrypt_credentials(creds_json: str) -> str:
    return fernet.encrypt(creds_json.encode()).decode()

def decrypt_credentials(encrypted_text: str) -> str:
    return fernet.decrypt(encrypted_text.encode()).decode()

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key:
            return jsonify({"error": "API Key requerida en el header 'x-api-key'"}), 401
            
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Buscar el usuario con esa API Key
            cur.execute("SELECT id, email FROM users WHERE api_key = %s", (api_key,))
            user = cur.fetchone()
            
            if not user:
                return jsonify({"error": "API Key inválida"}), 401
                
            # Cargar preferencias del usuario
            cur.execute("SELECT prompt_style, theme_colors, ai_model, company_info, database_schema, logo_path FROM user_preferences WHERE user_id = %s", (user['id'],))
            prefs = cur.fetchone() or {}
            
            # Añadir la info del usuario al objeto request de Flask para usarlo en el endpoint
            request.user = user
            request.user_preferences = prefs
            
            cur.close()
            conn.close()
            
        except Exception as e:
            return jsonify({"error": f"Error de autenticación: {str(e)}"}), 500
            
        return f(*args, **kwargs)
    return decorated_function
