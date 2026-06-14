"""
Blueprints de Flask para endpoints de base de datos
"""

import os
from flask import Blueprint, request, jsonify, send_file
from GR_DataBase.queries import DatabaseQueries

# Crear blueprint
database_bp = Blueprint('database', __name__, url_prefix='/database')


@database_bp.route('/connect', methods=['POST'])
def connect():
    """
    Conecta a la base de datos.
    
    Body JSON:
    {
        "database": "nombre_base_datos"  // opcional
    }
    """
    try:
        data = request.get_json() or {}
        database = data.get('database')
        
        db_queries = DatabaseQueries()
        success = db_queries.connect(database)
        db_queries.disconnect()
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Conectado a la base de datos{' ' + database if database else ''}"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "No se pudo conectar a la base de datos"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@database_bp.route('/tables', methods=['GET'])
def get_tables():
    """
    Obtiene la lista de tablas en la base de datos.
    
    Query params:
    - database: nombre de la base de datos (opcional)
    """
    try:
        database = request.args.get('database')
        
        with DatabaseQueries() as db_queries:
            db_queries.connect(database)
            tables = db_queries.db.get_tables()
        
        return jsonify({
            "status": "success",
            "tables": tables,
            "count": len(tables)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@database_bp.route('/columns/<table_name>', methods=['GET'])
def get_columns(table_name):
    """
    Obtiene las columnas de una tabla.
    
    Query params:
    - database: nombre de la base de datos (opcional)
    """
    try:
        database = request.args.get('database')
        
        with DatabaseQueries() as db_queries:
            db_queries.connect(database)
            columns = db_queries.db.get_columns(table_name)
        
        # Formatear columnas
        columns_info = [
            {
                "name": col[0],
                "type": col[1],
                "nullable": col[2] == "YES"
            }
            for col in columns
        ]
        
        return jsonify({
            "status": "success",
            "table": table_name,
            "columns": columns_info,
            "count": len(columns_info)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@database_bp.route('/query', methods=['POST'])
def execute_query():
    """
    Ejecuta una consulta SQL.
    
    Body JSON:
    {
        "query": "SELECT * FROM tabla",
        "database": "nombre_base_datos"  // opcional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Se requiere el campo 'query'"
            }), 400
        
        query = data['query']
        database = data.get('database')
        
        with DatabaseQueries() as db_queries:
            db_queries.connect(database)
            df = db_queries.execute_query(query)
        
        # Convertir DataFrame a JSON
        results = df.to_dict(orient='records')
        
        return jsonify({
            "status": "success",
            "data": results,
            "count": len(results),
            "columns": list(df.columns) if not df.empty else []
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@database_bp.route('/generate-query', methods=['POST'])
def generate_query():
    """
    Genera una consulta SQL usando IA basada en lenguaje natural.
    
    Body JSON:
    {
        "request": "descripción de lo que se quiere consultar",
        "database": "nombre_base_datos"  // opcional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({
                "status": "error",
                "message": "Se requiere el campo 'request'"
            }), 400
        
        user_request = data['request']
        database = data.get('database')
        
        with DatabaseQueries() as db_queries:
            db_queries.connect(database)
            query = db_queries.generate_query(user_request)
        
        return jsonify({
            "status": "success",
            "query": query
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@database_bp.route('/report', methods=['POST'])
def generate_report():
    """
    Genera un reporte basado en una consulta en lenguaje natural.
    
    Body JSON:
    {
        "request": "descripción de lo que se quiere consultar",
        "report_type": "excel|word|powerpoint",
        "database": "nombre_base_datos"  // opcional
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({
                "status": "error",
                "message": "Se requiere el campo 'request'"
            }), 400
        
        user_request = data['request']
        report_type = data.get('report_type', 'excel')
        database = data.get('database')
        
        with DatabaseQueries() as db_queries:
            db_queries.connect(database)
            report_path = db_queries.query_and_report(user_request, report_type)
        
        # Retornar el archivo
        return send_file(
            report_path,
            as_attachment=True,
            download_name=os.path.basename(report_path)
        )
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@database_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """
    Prueba la conexión a la base de datos con diferentes configuraciones.
    
    Body JSON:
    {
        "server": "127.0.0.1,1433",  // opcional
        "user": "usuario",           // opcional  
        "password": "password",      // opcional
        "database": "nombre_db"      // opcional
    }
    """
    try:
        data = request.get_json() or {}
        
        # Usar valores del request o del .env
        server = data.get('server', os.getenv('DB_SERVER', '127.0.0.1,1433'))
        user = data.get('user', os.getenv('DB_USER', 'Lecturas'))
        password = data.get('password', os.getenv('DB_PASSWORD', '@Lecturas2025@'))
        database = data.get('database', os.getenv('DB_NAME', ''))
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        print(f"[TEST] Probando conexión:")
        print(f"[TEST] Server: {server}")
        print(f"[TEST] User: {user}")
        print(f"[TEST] Database: {database or 'No especificada'}")
        print(f"[TEST] Driver: {driver}")
        
        # Construir connection string
        if database:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password};"
                "TrustServerCertificate=yes;"
                "Connection Timeout=10;"
                "Command Timeout=30;"
            )
        else:
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"UID={user};"
                f"PWD={password};"
                "TrustServerCertificate=yes;"
                "Connection Timeout=10;"
                "Command Timeout=30;"
            )
        
        print(f"[TEST] Connection string: {conn_str.replace(password, '***')}")
        
        # Intentar conexión
        import pyodbc
        connection = pyodbc.connect(conn_str, timeout=10)
        cursor = connection.cursor()
        
        # Probar una consulta simple
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        # Listar bases de datos disponibles
        cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
        databases = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "message": "Conexión exitosa",
            "server_version": version,
            "available_databases": databases,
            "connection_info": {
                "server": server,
                "user": user,
                "database": database or "No especificada",
                "driver": driver
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "connection_info": {
                "server": server,
                "user": user,
                "database": database or "No especificada",
                "driver": driver
            }
        }), 500


@database_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica el estado del módulo de base de datos."""
    return jsonify({
        "status": "success",
        "message": "Database module is running",
        "endpoints": [
            "/database/connect",
            "/database/tables",
            "/database/columns/<table_name>",
            "/database/query",
            "/database/generate-query",
            "/database/report",
            "/database/health"
        ]
    }), 200
