#!/usr/bin/env python3
import os
import subprocess
import time

def clear_screen():
    os.system('clear')

def print_header():
    clear_screen()
    print("=" * 60)
    print("                 GR DOCS - PANEL DE CONTROL")
    print("=" * 60)
    print()

def get_service_status():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'grdocs.service'], capture_output=True, text=True)
        if result.stdout.strip() == "active":
            return "\033[92mACTIVO (Corriendo)\033[0m"
        else:
            return "\033[91mINACTIVO (Detenido)\033[0m"
    except:
        return "Desconocido"

def run_command(command, use_sudo=False):
    if use_sudo:
        cmd = ['sudo'] + command
    else:
        cmd = command
    
    print(f"\nEjecutando: {' '.join(cmd)}")
    subprocess.run(cmd)
    input("\nPresiona Enter para continuar...")

def view_logs():
    print("\nAbriendo logs en tiempo real. Presiona Ctrl+C para salir y volver al menú.")
    time.sleep(1)
    try:
        subprocess.run(['sudo', 'journalctl', '-u', 'grdocs.service', '-f'])
    except KeyboardInterrupt:
        pass

def manage_users():
    clear_screen()
    print("=" * 60)
    print("                 ADMINISTRAR USUARIOS")
    print("=" * 60)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database="grdocs_saas",
            user="postgres",
            cursor_factory=RealDictCursor
        )
        cur = conn.cursor()
        
        cur.execute("SELECT id, email, username, is_approved FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
        
        if not users:
            print("\nNo hay usuarios registrados.")
        else:
            print(f"\n{'ID (corto)':<10} | {'Email':<25} | {'Username':<15} | {'Estado'}")
            print("-" * 65)
            for u in users:
                short_id = str(u['id'])[:8]
                estado = "\033[92mAprobado\033[0m" if u['is_approved'] else "\033[91mPendiente\033[0m"
                print(f"{short_id:<10} | {str(u['email'])[:25]:<25} | {str(u['username'])[:15]:<15} | {estado}")
                
            print("\nOpciones:")
            print("1. Aprobar usuario (por Email o ID)")
            print("2. Volver al menú principal")
            
            opt = input("\nElige una opción: ")
            if opt == '1':
                target = input("Ingresa el Email o inicio del ID del usuario: ")
                cur.execute("UPDATE users SET is_approved = TRUE WHERE email = %s OR id::text LIKE %s RETURNING email", (target, target + '%'))
                updated = cur.fetchone()
                conn.commit()
                if updated:
                    print(f"\n\033[92m¡Usuario {updated['email']} aprobado exitosamente!\033[0m")
                else:
                    print("\n\033[91mNo se encontró el usuario.\033[0m")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"\nError al conectar con la base de datos: {e}")
        print("Asegúrate de que 'psycopg2' esté instalado en este entorno.")
        
    input("\nPresiona Enter para continuar...")

def main():
    while True:
        print_header()
        print(f"Estado de la API: {get_service_status()}\n")
        print("Opciones:")
        print("  1. Ver estado detallado de la API")
        print("  2. Ver consola en tiempo real (Logs)")
        print("  3. Detener la API")
        print("  4. Iniciar la API")
        print("  5. Reiniciar la API")
        print("  6. Actualizar sistema (Git Pull)")
        print("  7. Administrar Usuarios (Aprobar API Keys)")
        print("  8. Salir")
        
        choice = input("\nElige una opción (1-8): ")
        
        if choice == '1':
            run_command(['systemctl', 'status', 'grdocs.service'])
        elif choice == '2':
            view_logs()
        elif choice == '3':
            run_command(['systemctl', 'stop', 'grdocs.service'], use_sudo=True)
        elif choice == '4':
            run_command(['systemctl', 'start', 'grdocs.service'], use_sudo=True)
        elif choice == '5':
            run_command(['systemctl', 'restart', 'grdocs.service'], use_sudo=True)
        elif choice == '6':
            run_command(['git', 'pull', 'origin', 'main'])
        elif choice == '7':
            manage_users()
        elif choice == '8':
            print("\nSaliendo del panel. La API seguirá corriendo en segundo plano.")
            break
        else:
            print("\nOpción inválida.")
            time.sleep(1)

if __name__ == "__main__":
    main()
