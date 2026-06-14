"""
Módulo de conexión a SQL Server usando pyodbc
"""

import os
import pyodbc
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class DatabaseConnection:
    """Maneja la conexión a SQL Server."""
    
    def __init__(self):
        """Inicializa la conexión con las credenciales del .env"""
        self.server = os.getenv('DB_SERVER', '127.0.0.1,1433')
        self.user = os.getenv('DB_USER', 'Lecturas')
        self.password = os.getenv('DB_PASSWORD', '@Lecturas2025@')
        self.database = os.getenv('DB_NAME', '')
        self.driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        self.connection: Optional[pyodbc.Connection] = None
        self.cursor: Optional[pyodbc.Cursor] = None
    
    def connect(self, database: str = None) -> bool:
        """
        Establece la conexión a la base de datos.
        
        Args:
            database: Nombre de la base de datos (opcional, usa DB_NAME del .env si no se especifica)
            
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            db_name = database or self.database
            
            # Construir connection string con timeouts mejorados
            if db_name:
                conn_str = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"DATABASE={db_name};"
                    f"UID={self.user};"
                    f"PWD={self.password};"
                    "TrustServerCertificate=yes;"
                    "Connection Timeout=30;"
                    "Command Timeout=60;"
                )
            else:
                # Conexión sin especificar base de datos
                conn_str = (
                    f"DRIVER={{{self.driver}}};"
                    f"SERVER={self.server};"
                    f"UID={self.user};"
                    f"PWD={self.password};"
                    "TrustServerCertificate=yes;"
                    "Connection Timeout=30;"
                    "Command Timeout=60;"
                )
            
            print(f"[DatabaseConnection] Intentando conectar a {self.server}...")
            print(f"[DatabaseConnection] Usuario: {self.user}")
            print(f"[DatabaseConnection] Base de datos: {db_name or 'No especificada'}")
            
            self.connection = pyodbc.connect(conn_str, timeout=30)
            self.cursor = self.connection.cursor()
            
            print(f"[DatabaseConnection] Conectado exitosamente a {self.server}")
            if db_name:
                print(f"[DatabaseConnection] Base de datos: {db_name}")
            
            return True
            
        except pyodbc.Error as e:
            print(f"[DatabaseConnection] Error al conectar: {e}")
            print(f"[DatabaseConnection] SUGERENCIA: Verifica que SQL Server esté corriendo en {self.server}")
            print(f"[DatabaseConnection] SUGERENCIA: Verifica las credenciales: usuario={self.user}")
            return False
    
    def disconnect(self):
        """Cierra la conexión a la base de datos."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("[DatabaseConnection] Desconectado exitosamente")
        except Exception as e:
            print(f"[DatabaseConnection] Error al desconectar: {e}")
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Lista de tuplas con los resultados
        """
        try:
            if not self.cursor:
                raise Exception("No hay conexión activa. Llama a connect() primero.")
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            return results
            
        except pyodbc.Error as e:
            print(f"[DatabaseConnection] Error al ejecutar consulta: {e}")
            return []
    
    def execute_non_query(self, query: str, params: tuple = None) -> int:
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Número de filas afectadas
        """
        try:
            if not self.cursor:
                raise Exception("No hay conexión activa. Llama a connect() primero.")
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor.rowcount
            
        except pyodbc.Error as e:
            print(f"[DatabaseConnection] Error al ejecutar consulta: {e}")
            self.connection.rollback()
            return 0
    
    def get_tables(self) -> list:
        """
        Obtiene la lista de tablas en la base de datos actual.
        
        Returns:
            Lista de nombres de tablas
        """
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        results = self.execute_query(query)
        return [row[0] for row in results]
    
    def get_columns(self, table_name: str) -> list:
        """
        Obtiene la lista de columnas de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de tuplas (nombre_columna, tipo_dato, es_nullable)
        """
        query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        results = self.execute_query(query, (table_name,))
        return [(row[0], row[1], row[2]) for row in results]
    
    def __enter__(self):
        """Soporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del context manager."""
        self.disconnect()
    
    def __repr__(self) -> str:
        status = "conectado" if self.connection else "desconectado"
        return f"DatabaseConnection(server={self.server}, status={status})"
