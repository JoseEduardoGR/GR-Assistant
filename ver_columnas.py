"""
Ver columnas de una tabla
"""

import os
import sys
from dotenv import load_dotenv
import pyodbc

load_dotenv()

db_server = os.getenv('DB_SERVER')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_driver = os.getenv('DB_DRIVER')

tabla = input("Nombre de la tabla (ej: PadronUsuariosAgua): ").strip()

try:
    conn_str = (
        f"DRIVER={{{db_driver}}};"
        f"SERVER={db_server};"
        f"DATABASE=DBAGUA;"
        f"UID={db_user};"
        f"PWD={db_password};"
        "TrustServerCertificate=yes;"
    )
    
    conn = pyodbc.connect(conn_str, timeout=5)
    cursor = conn.cursor()
    
    query = f"""
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{tabla}'
    ORDER BY ORDINAL_POSITION
    """
    
    cursor.execute(query)
    
    print(f"\nColumnas de {tabla}:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:40} {row[1]:20} {row[2]:10} {row[3] if row[3] else ''}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
