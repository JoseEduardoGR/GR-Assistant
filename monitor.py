#!/usr/bin/env python3
import os
from colorama import init, Fore, Style
import psycopg2
from psycopg2.extras import RealDictCursor

init(autoreset=True)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database="grdocs_saas",
        user="postgres",
        cursor_factory=RealDictCursor
    )

def main():
    print(Fore.CYAN + Style.BRIGHT + "===============================================================================================================")
    print(Fore.CYAN + Style.BRIGHT + "                                       GR Docs - Monitor de Usuarios                                       ")
    print(Fore.CYAN + Style.BRIGHT + "===============================================================================================================\n")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.email, u.api_key, u.created_at, p.ai_model 
            FROM users u
            LEFT JOIN user_preferences p ON u.id = p.user_id
            ORDER BY u.created_at DESC
        """)
        users = cur.fetchall()
        
        if not users:
            print(Fore.YELLOW + "No hay usuarios registrados aún.")
            return
            
        print(f"{Fore.YELLOW}{'Email':<30} | {'API Key':<25} | {'Modelo Preferido':<40} | {'Fecha Registro'}{Style.RESET_ALL}")
        print("-" * 120)
        
        for user in users:
            email = user['email']
            api_key = user['api_key']
            model = user['ai_model'] or "Predeterminado (settings.yaml)"
            created = user['created_at'].strftime("%Y-%m-%d %H:%M:%S") if user['created_at'] else "Desconocida"
            
            print(f"{email:<30} | {api_key:<25} | {Fore.GREEN}{model:<40}{Style.RESET_ALL} | {created}")
            
        print("\n" + "=" * 120)
        cur.close()
        conn.close()
        
    except Exception as e:
        print(Fore.RED + f"Error al conectar con la base de datos: {e}")

if __name__ == "__main__":
    main()
