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
        print("  7. Salir")
        
        choice = input("\nElige una opción (1-7): ")
        
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
            print("\nSaliendo del panel. La API seguirá corriendo en segundo plano.")
            break
        else:
            print("\nOpción inválida.")
            time.sleep(1)

if __name__ == "__main__":
    main()
