"""
Módulo de conexión a Base de Datos usando SQLAlchemy
"""

import os
from sqlalchemy import create_engine, text
from typing import Optional

class DatabaseConnection:
    """Maneja la conexión a cualquier Base de Datos mediante SQLAlchemy."""
    
    def __init__(self, connection_string: str = None):
        """Inicializa la conexión."""
        self.connection_string = connection_string
        self.engine = None
        self.connection = None
    
    def connect(self, connection_string: str = None) -> bool:
        """Establece la conexión a la base de datos."""
        try:
            conn_str = connection_string or self.connection_string
            if not conn_str:
                print("[DatabaseConnection] Error: connection_string no proporcionada.")
                return False
                
            print(f"[DatabaseConnection] Intentando conectar usando SQLAlchemy...")
            
            # Crear engine
            self.engine = create_engine(conn_str, pool_pre_ping=True)
            self.connection = self.engine.connect()
            
            print(f"[DatabaseConnection] Conectado exitosamente")
            return True
            
        except Exception as e:
            print(f"[DatabaseConnection] Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión a la base de datos."""
        try:
            if self.connection:
                self.connection.close()
            if self.engine:
                self.engine.dispose()
            print("[DatabaseConnection] Desconectado exitosamente")
        except Exception as e:
            print(f"[DatabaseConnection] Error al desconectar: {e}")
    
    def execute_query(self, query: str, params: dict = None) -> tuple:
        """Ejecuta una consulta SELECT y retorna (filas, columnas)."""
        try:
            if not self.connection:
                raise Exception("No hay conexión activa. Llama a connect() primero.")
            
            result = self.connection.execute(text(query), params or {})
            columns = list(result.keys())
            rows = [tuple(row) for row in result.fetchall()]
            return rows, columns
            
        except Exception as e:
            print(f"[DatabaseConnection] Error al ejecutar consulta: {e}")
            raise e  # Lanzamos el error para que la IA lo vea y pueda autocorregirse
            
    def execute_non_query(self, query: str, params: dict = None) -> int:
        """Ejecuta una consulta INSERT, UPDATE o DELETE."""
        try:
            if not self.connection:
                raise Exception("No hay conexión activa. Llama a connect() primero.")
            
            with self.connection.begin():
                result = self.connection.execute(text(query), params or {})
                return result.rowcount
            
        except Exception as e:
            print(f"[DatabaseConnection] Error al ejecutar consulta: {e}")
            raise e
    
    def get_tables(self) -> list:
        """Obtiene la lista de tablas en la base de datos actual."""
        # Consulta genérica de ANSI SQL para información de tablas
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        try:
            rows, _ = self.execute_query(query)
            return [row[0] for row in rows]
        except Exception as e:
            print(f"[DatabaseConnection] Warning get_tables: {e}")
            return []
    
    def get_columns(self, table_name: str) -> list:
        """Obtiene la lista de columnas de una tabla."""
        query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """
        try:
            rows, _ = self.execute_query(query, {"table_name": table_name})
            return [(row[0], row[1], row[2]) for row in rows]
        except:
            return []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def __repr__(self) -> str:
        status = "conectado" if self.connection else "desconectado"
        return f"DatabaseConnection(status={status})"
