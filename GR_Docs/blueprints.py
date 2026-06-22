import os
import yaml
from flask import Blueprint, request, jsonify, send_file, Response
from colorama import Fore

# Imports relativos desde el paquete GR_Docs
from .doc.word import WordScriptGenerator
from .xlsx.excel import ExcelScriptGenerator
from .pptx.powerpoint import PowerPointScriptGenerator
from .security import require_api_key, get_db_connection, encrypt_credentials, require_admin_key

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


@api_bp.route('/cli', methods=['GET'])
@api_bp.route('/cli.ps1', methods=['GET'])
def cli_menu():
    """Sirve el script Bash o PowerShell TUI para que los clientes lo ejecuten."""
    import os
    if request.path.endswith('.ps1'):
        script_name = 'cli.ps1'
    else:
        user_agent = request.headers.get('User-Agent', '').lower()
        if 'windows' in user_agent or 'powershell' in user_agent:
            script_name = 'cli.ps1'
        else:
            script_name = 'cli.sh'
            
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), script_name)
    return send_file(script_path, mimetype='text/plain')


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


def extract_user_files(user_id):
    """
    Extrae los archivos de la base de datos para el usuario y los guarda localmente.
    Retorna una lista de diccionarios con el nombre semántico y la ruta física.
    """
    import os
    from pathlib import Path
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT file_name, file_data FROM user_files WHERE user_id = %s", (user_id,))
    files = cur.fetchall()
    cur.close()
    conn.close()
    
    if not files:
        return []
        
    # Crear directorio temporal para el usuario
    base_dir = Path(os.path.abspath(__file__)).parent / "cache" / "users" / str(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_files = []
    for f in files:
        semantic_name = f['file_name']
        file_path = base_dir / semantic_name
        
        with open(file_path, 'wb') as out_file:
            out_file.write(f['file_data'])
            
        extracted_files.append({
            "name": semantic_name,
            "path": str(file_path)
        })
        
    return extracted_files

def is_database_required(prompt: str, user_preferences: dict = None) -> bool:
    """Decide de forma inteligente si la petición requiere consultar la base de datos."""
    from assets.engine import OpenRouterEngine
    engine = OpenRouterEngine(verbose=False)
    
    if user_preferences and 'ai_model' in user_preferences:
        engine.model = user_preferences['ai_model']
        
    engine.context = """Eres un enrutador inteligente para una API de generación de documentos.
Tu única tarea es analizar la instrucción del usuario y decidir si para cumplirla se requiere consultar, extraer o leer datos de una Base de Datos SQL conectada, o si se puede cumplir generando un texto libre (inventado por la IA).
Ejemplos de DATABASE_YES (requiere BD): "reporte de ventas", "calificaciones de alumnos", "dame los 10 mejores clientes".
Ejemplos de DATABASE_NO (texto libre): "crea una carta de bienvenida", "redacta un documento sobre ética", "haz un contrato".
Responde EXCLUSIVAMENTE con la palabra "DATABASE_YES" si requiere explícitamente extraer datos estructurados.
Responde EXCLUSIVAMENTE con la palabra "DATABASE_NO" si es un documento de texto libre, académico o creativo."""
    response = engine.process(prompt)
    if not response:
        return False
    return "DATABASE_YES" in response.strip().upper()

def try_database_generation(user_id, user_request, report_type, user_files_context, should_download, data):
    """Intenta generar el reporte usando la BD. Retorna (True, final_path) o (False, error_response)."""
    from GR_Docs.security import get_db_connection
    from GR_DataBase.blueprints import decrypt_credentials
    from GR_DataBase.queries import DatabaseQueries
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT encrypted_credentials FROM client_databases WHERE user_id = %s", (user_id,))
    record = cur.fetchone()
    cur.close()
    conn.close()
    
    if not record:
        return False, jsonify({"success": False, "error": "La IA determinó que necesitas extraer datos, pero no se encontraron credenciales de base de datos. Configúralas con /client-db primero."}), 400
        
    conn_string = decrypt_credentials(record['encrypted_credentials'])
    
    with DatabaseQueries() as db_queries:
        if not db_queries.connect(conn_string):
            return False, jsonify({"success": False, "error": "Fallo al conectar a tu base de datos configurada."}), 500
            
        try:
            report_path = db_queries.query_and_report(user_request, report_type, user_files_context)
            if should_download:
                import os
                import shutil
                custom_name = data.get('filename')
                if custom_name:
                    if not custom_name.endswith(f".{report_type[:4]}"): # approximate extension
                        if report_type == "excel": ext = ".xlsx"
                        elif report_type == "word": ext = ".docx"
                        elif report_type == "powerpoint": ext = ".pptx"
                        else: ext = ""
                        custom_name += ext
                    
                    new_path = os.path.join(os.path.dirname(report_path), custom_name)
                    shutil.copy2(report_path, new_path)
                    report_path = new_path
            return True, report_path, 200
        except Exception as e:
            return False, jsonify({"success": False, "error": f"Error en la base de datos: {str(e)}"}), 500


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
        
        print(Fore.CYAN + f"[API] Analizando petición Word...")
        user_files_context = extract_user_files(request.user['id'])
        
        # AGENTIC ROUTER: Decidir si requiere BD
        is_db = is_database_required(user_request, getattr(request, 'user_preferences', {}))
        
        if is_db:
            print(Fore.CYAN + f"[API] Router -> Modo Base de Datos Detectado")
            success, result, status_code = try_database_generation(request.user['id'], user_request, "word", user_files_context, should_download, data)
            if not success:
                return result, status_code
            final_path = result
            script_path = "Generado por SQL Agent"
        else:
            print(Fore.CYAN + f"[API] Router -> Modo Texto Libre Detectado")
            # Obtener generador
            word_gen = get_word_generator()
            
            # Generar y ejecutar
            script_path, docx_path = word_gen.generate_and_execute(
                user_request, 
                user_preferences=getattr(request, 'user_preferences', {}),
                user_files_context=user_files_context
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
        
        print(Fore.CYAN + f"[API] Analizando petición Excel...")
        user_files_context = extract_user_files(request.user['id'])
        
        # AGENTIC ROUTER: Decidir si requiere BD
        is_db = is_database_required(user_request, getattr(request, 'user_preferences', {}))
        
        if is_db:
            print(Fore.CYAN + f"[API] Router -> Modo Base de Datos Detectado")
            success, result, status_code = try_database_generation(request.user['id'], user_request, "excel", user_files_context, should_download, data)
            if not success:
                return result, status_code
            final_path = result
            script_path = "Generado por SQL Agent"
        else:
            print(Fore.CYAN + f"[API] Router -> Modo Texto Libre Detectado")
            # Obtener generador
            excel_gen = get_excel_generator()
            
            # Generar y ejecutar
            script_path, xlsx_path = excel_gen.generate_and_execute(
                user_request,
                user_preferences=getattr(request, 'user_preferences', {}),
                user_files_context=user_files_context
            )
            
            # Verificar si hubo error
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
        
        print(Fore.CYAN + f"[API] Analizando petición PowerPoint...")
        user_files_context = extract_user_files(request.user['id'])
        
        # AGENTIC ROUTER: Decidir si requiere BD
        is_db = is_database_required(user_request, getattr(request, 'user_preferences', {}))
        
        if is_db:
            print(Fore.CYAN + f"[API] Router -> Modo Base de Datos Detectado")
            success, result, status_code = try_database_generation(request.user['id'], user_request, "powerpoint", user_files_context, should_download, data)
            if not success:
                return result, status_code
            final_path = result
            script_path = "Generado por SQL Agent"
        else:
            print(Fore.CYAN + f"[API] Router -> Modo Texto Libre Detectado")
            # Obtener generador
            pptx_gen = get_pptx_generator()
            
            # Generar y ejecutar
            script_path, pptx_path = pptx_gen.generate_and_execute(
                user_request,
                user_preferences=getattr(request, 'user_preferences', {}),
                user_files_context=user_files_context
            )
            
            # Verificar si hubo error
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

import secrets
import psycopg2

@api_bp.route('/register', methods=['POST'])
def register_user():
    """Registra un nuevo usuario y devuelve una API Key segura."""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'username' not in data:
            return jsonify({"success": False, "error": "Los campos 'email' y 'username' son requeridos"}), 400
            
        email = data['email'].strip()
        username = data['username'].strip()
        
        if not email or not username:
            return jsonify({"success": False, "error": "El 'email' y 'username' no pueden estar vacíos"}), 400
            
        # Generar API key segura (ej. gr_A8xN...)
        api_key = "gr_" + secrets.token_urlsafe(32)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO users (email, username, api_key) VALUES (%s, %s, %s) RETURNING id",
                (email, username, api_key)
            )
            user_id = cur.fetchone()['id']
            conn.commit()
            
            return jsonify({
                "success": True, 
                "message": "Usuario registrado exitosamente. GUARDA TU API KEY, NO PODRÁS VERLA DE NUEVO.",
                "email": email,
                "api_key": api_key,
                "user_id": user_id
            }), 201
            
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return jsonify({"success": False, "error": "El email ya está registrado"}), 409
            
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
        prompt_style = data.get('prompt_style', request.user_preferences.get('prompt_style', ''))
        theme_colors = data.get('theme_colors', request.user_preferences.get('theme_colors', '{}'))
        ai_model = data.get('ai_model', request.user_preferences.get('ai_model'))
        company_info = data.get('company_info', request.user_preferences.get('company_info', ''))
        database_schema = data.get('database_schema', request.user_preferences.get('database_schema', ''))
        logo_path = data.get('logo_path', request.user_preferences.get('logo_path', ''))
        
        ALLOWED_MODELS = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "deepseek/deepseek-chat:free",
            "mistralai/mistral-nemo:free",
            "nex-agi/nex-n2-pro:free",
            "cohere/north-mini-code:free"
        ]
        
        if ai_model and ai_model not in ALLOWED_MODELS:
            return jsonify({"error": f"Modelo no permitido. Debe ser uno de: {ALLOWED_MODELS}"}), 400
        
        import json
        if isinstance(theme_colors, dict):
            theme_colors = json.dumps(theme_colors)
            
        cur.execute("""
            INSERT INTO user_preferences (user_id, prompt_style, theme_colors, ai_model, company_info, database_schema, logo_path) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE 
            SET prompt_style = EXCLUDED.prompt_style, 
                theme_colors = EXCLUDED.theme_colors, 
                ai_model = EXCLUDED.ai_model,
                company_info = EXCLUDED.company_info,
                database_schema = EXCLUDED.database_schema,
                logo_path = EXCLUDED.logo_path
        """, (user_id, prompt_style, theme_colors, ai_model, company_info, database_schema, logo_path))
        
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
        
    semantic_name = request.form.get('name', '').strip()
    if semantic_name:
        import os
        _, ext = os.path.splitext(file.filename)
        if not ext:
            ext = '.png'
        if not semantic_name.endswith(ext):
            semantic_name += ext
    else:
        semantic_name = file.filename
        
    try:
        file_data = file.read()
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO user_files (user_id, file_name, file_data) VALUES (%s, %s, %s)",
            (request.user['id'], semantic_name, psycopg2.Binary(file_data))
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"success": True, "message": f"Archivo guardado exitosamente con nombre: {semantic_name}"}), 200
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
        
        return jsonify({"success": True, "message": "Conexión a BD guardada exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al guardar credenciales: {str(e)}"}), 500

@api_bp.route('/admin/approve', methods=['POST'])
@require_admin_key
def approve_user():
    """Aprueba un usuario pendiente mediante su email."""
    data = request.json
    target_email = data.get('email')
    
    if not target_email:
        return jsonify({"error": "Debe proporcionar el email del usuario a aprobar"}), 400
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("UPDATE users SET is_approved = TRUE WHERE email = %s RETURNING id", (target_email,))
        updated = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        if updated:
            return jsonify({"success": True, "message": f"Usuario {target_email} aprobado correctamente"})
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Error al aprobar usuario: {str(e)}"}), 500

@api_bp.route('/admin/logs/stream')
@require_admin_key
def stream_logs():
    """Stream de consola en tiempo real (SSE)."""
    def generate():
        import subprocess
        process = subprocess.Popen(['journalctl', '-u', 'grdocs.service', '-f', '-n', '50'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        try:
            while True:
                line = process.stdout.readline()
                if line:
                    yield f"data: {line}\n\n"
                else:
                    import time
                    time.sleep(0.1)
        except GeneratorExit:
            process.terminate()
            
    return Response(generate(), mimetype='text/event-stream')

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
        print("[Webhook] Reiniciando servidor en 2 segundos...")
        # Forzar el reinicio cerrando el proceso actual (systemd lo reiniciará automáticamente)
        time.sleep(2)
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
