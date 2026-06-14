import os
import yaml
from flask import Blueprint, request, jsonify, send_file
from colorama import Fore

# Imports relativos desde el paquete GR_Docs
from .doc.word import WordScriptGenerator
from .xlsx.excel import ExcelScriptGenerator
from .pptx.powerpoint import PowerPointScriptGenerator
from .security import require_api_key, get_db_connection, encrypt_credentials

# Cargar configuración
with open("settings.yaml") as f:
    settings = yaml.safe_load(f)

# Crear blueprints
api_bp = Blueprint('api', __name__)

# Generadores (se inicializan bajo demanda)
_word_gen = None
_excel_gen = None
_pptx_gen = None


def check_script_for_errors(script_path):
    """
    Verifica si el script generado contiene errores de API.
    Retorna (has_error, error_response) donde error_response es None si no hay error.
    """
    if not script_path or not os.path.exists(script_path):
        return False, None
    
    try:
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Detectar rate limit
        if '[Error HTTP 429]' in script_content or 'rate-limited' in script_content.lower():
            return True, jsonify({
                "success": False,
                "error": "El modelo de IA está temporalmente limitado por tasa de uso",
                "error_type": "rate_limit",
                "suggestion": "Intenta de nuevo en unos segundos o cambia el modelo en settings.yaml",
                "retry_after": 12,
                "current_model": settings.get("model", "unknown")
            }), 429
        
        # Detectar otros errores de API
        if '[Error' in script_content and 'HTTP' in script_content:
            return True, jsonify({
                "success": False,
                "error": "Error al comunicarse con el modelo de IA",
                "error_type": "api_error",
                "suggestion": "Verifica tu API key o intenta con otro modelo",
                "current_model": settings.get("model", "unknown")
            }), 500
        
        return False, None
    except Exception:
        return False, None


def handle_runtime_error(e, dependency_name="Node.js"):
    """Maneja errores de runtime y retorna respuesta JSON apropiada."""
    error_msg = str(e)
    
    # Detectar error de sintaxis de ES6 modules (Node.js antiguo)
    if 'SyntaxError: Unexpected token' in error_msg and 'import' in error_msg:
        return jsonify({
            "success": False,
            "error": "Versión de Node.js incompatible (requiere v14+)",
            "error_type": "dependency_version_error",
            "details": "Tu versión de Node.js no soporta módulos ES6",
            "suggestion": "Actualiza Node.js a la versión 14 o superior: https://nodejs.org/",
            "current_nodejs_version": "< v14 (detectado por error de sintaxis)"
        }), 500
    
    if 'rate-limited' in error_msg.lower() or '429' in error_msg:
        return jsonify({
            "success": False,
            "error": "Modelo temporalmente limitado por tasa de uso",
            "error_type": "rate_limit",
            "details": error_msg,
            "suggestion": "Espera unos segundos o cambia el modelo en settings.yaml",
            "retry_after": 12,
            "current_model": settings.get("model", "unknown")
        }), 429
    elif f"no such file or directory: '{dependency_name.lower()}'" in error_msg.lower() or f"command not found: {dependency_name.lower()}" in error_msg.lower():
        return jsonify({
            "success": False,
            "error": f"{dependency_name} no está instalado o no está en el PATH",
            "error_type": "dependency_error",
            "suggestion": f"Instala {dependency_name}"
        }), 500
    else:
        return jsonify({
            "success": False,
            "error": error_msg,
            "error_type": "runtime_error"
        }), 500


def get_word_generator():
    """Obtener generador de Word (lazy loading)."""
    global _word_gen
    if _word_gen is None:
        _word_gen = WordScriptGenerator()
    return _word_gen


def get_excel_generator():
    """Obtener generador de Excel (lazy loading)."""
    global _excel_gen
    if _excel_gen is None:
        _excel_gen = ExcelScriptGenerator()
    return _excel_gen


def get_pptx_generator():
    """Obtener generador de PowerPoint (lazy loading)."""
    global _pptx_gen
    if _pptx_gen is None:
        _pptx_gen = PowerPointScriptGenerator()
    return _pptx_gen


@api_bp.route('/', methods=['GET'])
def home():
    """Endpoint de bienvenida con documentación de la API."""
    return jsonify({
        "name": "GR Docs API",
        "version": "1.0.0",
        "description": "API para generar documentos Word, Excel y PowerPoint usando IA",
        "endpoints": {
            "POST /docx": "Generar documento Word (.docx)",
            "POST /xlsx": "Generar archivo Excel (.xlsx)",
            "POST /pptx": "Generar presentación PowerPoint (.pptx)",
            "GET /health": "Verificar estado del servidor"
        },
        "documentation": "https://github.com/JoseEduardoGR/GRDocs"
    })


@api_bp.route('/health', methods=['GET'])
def health():
    """Verificar estado del servidor."""
    return jsonify({
        "status": "healthy",
        "model": settings.get("model", "unknown"),
        "generators": {
            "word": "ready",
            "excel": "ready",
            "powerpoint": "ready"
        }
    })


@api_bp.route('/docx', methods=['POST'])
@require_api_key
def generate_docx():
    """
    Generar documento Word (.docx)
    
    Body JSON:
    {
        "request": "Descripción del documento a generar",
        "download": true/false (opcional, default: false)
    }
    
    Response:
    {
        "success": true,
        "script_path": "ruta del script generado",
        "document_path": "ruta del documento generado",
        "message": "Documento generado exitosamente"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'request' es requerido",
                "error_type": "validation_error"
            }), 400
        
        user_request = data['request']
        should_download = data.get('download', False)
        
        print(Fore.CYAN + f"[API] Generando documento Word...")
        print(Fore.WHITE + f"Solicitud: {user_request[:100]}...")
        
        # Obtener generador
        word_gen = get_word_generator()
        
        # Generar y ejecutar
        script_path, docx_path = word_gen.generate_and_execute(
            user_request, 
            user_preferences=getattr(request, 'user_preferences', {})
        )
        
        # Verificar si hubo error en la generación del script
        has_error, error_response = check_script_for_errors(script_path)
        if has_error:
            print(Fore.RED + f"[API] ✗ Error detectado en el script generado")
            return error_response
        
        # Renombrar si se solicita descarga
        if should_download:
            custom_name = data.get('filename')
            final_path = word_gen.download(docx_path, custom_name)
        else:
            final_path = docx_path
        
        print(Fore.GREEN + f"[API] ✓ Documento generado: {final_path}")
        
        response = {
            "success": True,
            "script_path": script_path,
            "document_path": final_path,
            "message": "Documento Word generado exitosamente"
        }
        
        # Si se solicita descarga, enviar el archivo
        if should_download and data.get('send_file', False):
            return send_file(
                final_path,
                as_attachment=True,
                download_name=os.path.basename(final_path),
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        return jsonify(response), 200
        
    except RuntimeError as e:
        print(Fore.RED + f"[API] ✗ RuntimeError: {str(e)}")
        return handle_runtime_error(e, "Node.js")
            
    except FileNotFoundError as e:
        print(Fore.RED + f"[API] ✗ FileNotFoundError: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "file_not_found",
            "suggestion": "Verifica que todas las dependencias estén instaladas"
        }), 500
        
    except Exception as e:
        print(Fore.RED + f"[API] ✗ Error inesperado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "unknown_error"
        }), 500


@api_bp.route('/xlsx', methods=['POST'])
@require_api_key
def generate_xlsx():
    """
    Generar archivo Excel (.xlsx)
    
    Body JSON:
    {
        "request": "Descripción del archivo Excel a generar",
        "download": true/false (opcional, default: false)
    }
    
    Response:
    {
        "success": true,
        "script_path": "ruta del script generado",
        "file_path": "ruta del archivo generado",
        "message": "Archivo Excel generado exitosamente"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'request' es requerido",
                "error_type": "validation_error"
            }), 400
        
        user_request = data['request']
        should_download = data.get('download', False)
        
        print(Fore.CYAN + f"[API] Generando archivo Excel...")
        print(Fore.WHITE + f"Solicitud: {user_request[:100]}...")
        
        # Obtener generador
        excel_gen = get_excel_generator()
        
        # Generar y ejecutar
        script_path, xlsx_path = excel_gen.generate_and_execute(
            user_request,
            user_preferences=getattr(request, 'user_preferences', {})
        )
        
        # Verificar si hubo error en la generación del script
        has_error, error_response = check_script_for_errors(script_path)
        if has_error:
            print(Fore.RED + f"[API] ✗ Error detectado en el script generado")
            return error_response
        
        # Renombrar si se solicita descarga
        if should_download:
            custom_name = data.get('filename')
            final_path = excel_gen.download(xlsx_path, custom_name)
        else:
            final_path = xlsx_path
        
        print(Fore.GREEN + f"[API] ✓ Archivo generado: {final_path}")
        
        response = {
            "success": True,
            "script_path": script_path,
            "file_path": final_path,
            "message": "Archivo Excel generado exitosamente"
        }
        
        # Si se solicita descarga, enviar el archivo
        if should_download and data.get('send_file', False):
            return send_file(
                final_path,
                as_attachment=True,
                download_name=os.path.basename(final_path),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        return jsonify(response), 200
        
    except RuntimeError as e:
        print(Fore.RED + f"[API] ✗ RuntimeError: {str(e)}")
        return handle_runtime_error(e, "Python")
            
    except FileNotFoundError as e:
        print(Fore.RED + f"[API] ✗ FileNotFoundError: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "file_not_found",
            "suggestion": "Verifica que todas las dependencias estén instaladas"
        }), 500
        
    except Exception as e:
        print(Fore.RED + f"[API] ✗ Error inesperado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "unknown_error"
        }), 500


@api_bp.route('/pptx', methods=['POST'])
@require_api_key
def generate_pptx():
    """
    Generar presentación PowerPoint (.pptx)
    
    Body JSON:
    {
        "request": "Descripción de la presentación a generar",
        "download": true/false (opcional, default: false)
    }
    
    Response:
    {
        "success": true,
        "script_path": "ruta del script generado",
        "presentation_path": "ruta de la presentación generada",
        "message": "Presentación PowerPoint generada exitosamente"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'request' es requerido",
                "error_type": "validation_error"
            }), 400
        
        user_request = data['request']
        should_download = data.get('download', False)
        
        print(Fore.CYAN + f"[API] Generando presentación PowerPoint...")
        print(Fore.WHITE + f"Solicitud: {user_request[:100]}...")
        
        # Obtener generador
        pptx_gen = get_pptx_generator()
        
        # Generar y ejecutar
        script_path, pptx_path = pptx_gen.generate_and_execute(
            user_request,
            user_preferences=getattr(request, 'user_preferences', {})
        )
        
        # Verificar si hubo error en la generación del script
        has_error, error_response = check_script_for_errors(script_path)
        if has_error:
            print(Fore.RED + f"[API] ✗ Error detectado en el script generado")
            return error_response
        
        # Renombrar si se solicita descarga
        if should_download:
            custom_name = data.get('filename')
            final_path = pptx_gen.download(pptx_path, custom_name)
        else:
            final_path = pptx_path
        
        print(Fore.GREEN + f"[API] ✓ Presentación generada: {final_path}")
        
        response = {
            "success": True,
            "script_path": script_path,
            "presentation_path": final_path,
            "message": "Presentación PowerPoint generada exitosamente"
        }
        
        # Si se solicita descarga, enviar el archivo
        if should_download and data.get('send_file', False):
            return send_file(
                final_path,
                as_attachment=True,
                download_name=os.path.basename(final_path),
                mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
            )
        
        return jsonify(response), 200
        
    except RuntimeError as e:
        print(Fore.RED + f"[API] ✗ RuntimeError: {str(e)}")
        return handle_runtime_error(e, "Node.js")
            
    except FileNotFoundError as e:
        print(Fore.RED + f"[API] ✗ FileNotFoundError: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "file_not_found",
            "suggestion": "Verifica que todas las dependencias estén instaladas"
        }), 500
        
    except Exception as e:
        print(Fore.RED + f"[API] ✗ Error inesperado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": "unknown_error"
        }), 500

# Nuevos Endpoints SaaS

@api_bp.route('/preferences', methods=['GET', 'POST'])
@require_api_key
def manage_preferences():
    """Gestiona las preferencias del usuario."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        user_id = request.user['id']
        
        if request.method == 'GET':
            return jsonify({"success": True, "preferences": request.user_preferences}), 200
            
        # Para POST
        data = request.get_json()
        prompt_style = data.get('prompt_style', '')
        theme_colors = data.get('theme_colors', '{}')
        ai_model = data.get('ai_model')
        
        ALLOWED_MODELS = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "deepseek/deepseek-chat:free",
            "mistralai/mistral-nemo:free",
            "nex-agi/nex-n2-pro:free"
        ]
        
        if ai_model and ai_model not in ALLOWED_MODELS:
            return jsonify({"error": f"Modelo no permitido. Debe ser uno de: {ALLOWED_MODELS}"}), 400
        
        import json
        if isinstance(theme_colors, dict):
            theme_colors = json.dumps(theme_colors)
            
        cur.execute("""
            INSERT INTO user_preferences (user_id, prompt_style, theme_colors, ai_model) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE 
            SET prompt_style = EXCLUDED.prompt_style, theme_colors = EXCLUDED.theme_colors, ai_model = EXCLUDED.ai_model
        """, (user_id, prompt_style, theme_colors, ai_model))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Preferencias actualizadas"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/files', methods=['POST'])
@require_api_key
def upload_file():
    """Sube un logo o plantilla del usuario a la DB."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    try:
        file_data = file.read()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO user_files (user_id, file_name, file_data) VALUES (%s, %s, %s)",
            (request.user['id'], file.filename, psycopg2.Binary(file_data))
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"success": True, "message": f"Archivo {file.filename} guardado exitosamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/client-db', methods=['POST'])
@require_api_key
def configure_client_db():
    """Configura la cadena de conexión de la DB del cliente (Enfoque A)."""
    try:
        data = request.get_json()
        conn_string = data.get('connection_string')
        if not conn_string:
            return jsonify({"error": "connection_string es requerido"}), 400
            
        encrypted = encrypt_credentials(conn_string)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO client_databases (user_id, encrypted_credentials) 
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE 
            SET encrypted_credentials = EXCLUDED.encrypted_credentials
        """, (request.user['id'], encrypted))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Credenciales de DB guardadas de forma segura"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

import subprocess
import threading
import sys
import time

def auto_update_task():
    """Ejecuta git pull y termina el proceso para que se reinicie (ej. vía systemd o gunicorn)."""
    try:
        print("[Webhook] Iniciando git pull...")
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        print("[Webhook] Actualizando dependencias...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("[Webhook] Reiniciando servidor...")
        # Forzar el reinicio cerrando el proceso actual
        os._exit(0)
    except Exception as e:
        print(f"[Webhook] Error durante la actualización: {e}")

@api_bp.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Webhook para auto-actualización cuando se hace un push en GitHub."""
    import hmac
    import hashlib
    
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "GRcode2026$")
    signature = request.headers.get('X-Hub-Signature-256')
    
    if not signature:
        return jsonify({"success": False, "error": "Falta la firma de GitHub"}), 401
        
    expected_signature = "sha256=" + hmac.new(
        secret.encode('utf-8'),
        request.get_data(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({"success": False, "error": "Firma inválida"}), 403

    # Ejecuta la actualización en un hilo en segundo plano para poder responder inmediatamente a GitHub
    threading.Thread(target=auto_update_task).start()
    return jsonify({"success": True, "message": "Actualización en progreso"}), 200

@api_bp.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas."""
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado",
        "available_endpoints": ["/", "/health", "/docx", "/xlsx", "/pptx"]
    }), 404


@api_bp.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos del servidor."""
    return jsonify({
        "success": False,
        "error": "Error interno del servidor"
    }), 500
