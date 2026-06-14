"""
Test de conexión a SQL Server
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 60)
print("Test de Conexión a SQL Server")
print("=" * 60)
print()

# Verificar pyodbc
try:
    import pyodbc
    print("✓ pyodbc instalado")
except ImportError:
    print("✗ pyodbc NO instalado")
    print("  Instala con: pip install pyodbc")
    sys.exit(1)

# Mostrar configuración
db_server = os.getenv('DB_SERVER', '127.0.0.1,1433')
db_user = os.getenv('DB_USER', 'Lecturas')
db_password = os.getenv('DB_PASSWORD', '@Lecturas2025@')
db_driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

print(f"Servidor: {db_server}")
print(f"Usuario: {db_user}")
print(f"Driver: {db_driver}")
print()

# Listar drivers disponibles
print("Drivers ODBC disponibles:")
drivers = pyodbc.drivers()
for driver in drivers:
    print(f"  - {driver}")
print()

# Intentar conexión
print("Conectando...")
try:
    conn_str = (
        f"DRIVER={{{db_driver}}};"
        f"SERVER={db_server};"
        f"UID={db_user};"
        f"PWD={db_password};"
        "TrustServerCertificate=yes;"
    )
    
    conn = pyodbc.connect(conn_str, timeout=5)
    cursor = conn.cursor()
    
    print("✓ Conexión exitosa!")
    print()
    
    # Listar bases de datos
    print("Bases de datos disponibles:")
    cursor.execute("SELECT name FROM sys.databases ORDER BY name")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    cursor.close()
    conn.close()
    
    print()
    print("=" * 60)
    print("✓ TEST EXITOSO")
    print("=" * 60)
    
except pyodbc.Error as e:
    print(f"✗ Error: {e}")
    print()
    print("Verifica:")
    print("  1. SQL Server está corriendo")
    print("  2. Credenciales en .env son correctas")
    print("  3. Driver ODBC está instalado")
    sys.exit(1)
