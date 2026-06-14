import yaml
from flask import Flask
from flask_cors import CORS
from colorama import Fore, init, Style
from .blueprints import api_bp

# Importar blueprint de base de datos
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GR_DataBase.blueprints import database_bp

init(autoreset=True)

# Cargar configuración
with open("settings.yaml") as f:
    settings = yaml.safe_load(f)


def check_nodejs_version():
    """Verifica que Node.js esté instalado y sea versión 14+."""
    try:
        import subprocess
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_str = result.stdout.strip()
            # Extraer número de versión (ej: "v10.19.0" -> 10)
            version_major = int(version_str.lstrip('v').split('.')[0])
            
            if version_major < 14:
                print(Fore.RED + f"⚠️  ADVERTENCIA: Node.js {version_str} detectado")
                print(Fore.YELLOW + f"   GR Docs requiere Node.js v14+ para módulos ES6")
                print(Fore.YELLOW + f"   Actualiza desde: https://nodejs.org/\n")
                return False
            else:
                print(Fore.GREEN + f"✓ Node.js {version_str} detectado")
                return True
        else:
            print(Fore.RED + "⚠️  Node.js no encontrado en el PATH")
            return False
    except FileNotFoundError:
        print(Fore.RED + "⚠️  Node.js no está instalado")
        return False
    except Exception as e:
        print(Fore.YELLOW + f"⚠️  No se pudo verificar versión de Node.js: {e}")
        return False


def create_app():
    """Crear y configurar la aplicación Flask."""
    app = Flask(__name__)
    CORS(app)  # Permitir CORS para todas las rutas
    
    # Registrar blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(database_bp)
    
    return app


def main():
    """Iniciar el servidor Flask."""
    port = settings.get('port', 8000)
    
    print(Fore.CYAN + Style.BRIGHT + "\n╔════════════════════════════════════════════════════════════════╗")
    print(Fore.CYAN + Style.BRIGHT + "║                    GR DOCS API SERVER                          ║")
    print(Fore.CYAN + Style.BRIGHT + "╚════════════════════════════════════════════════════════════════╝\n")
    
    # Verificar Node.js
    check_nodejs_version()
    
    print(Fore.YELLOW + f"🚀 Servidor iniciando en http://localhost:{port}")
    print(Fore.GREEN + f"📝 Modelo configurado: {settings.get('model', 'unknown')}\n")
    
    print(Fore.WHITE + "Endpoints disponibles:")
    print(Fore.CYAN + f"  GET  http://localhost:{port}/")
    print(Fore.CYAN + f"  GET  http://localhost:{port}/health")
    print(Fore.GREEN + f"  POST http://localhost:{port}/docx")
    print(Fore.GREEN + f"  POST http://localhost:{port}/xlsx")
    print(Fore.GREEN + f"  POST http://localhost:{port}/pptx")
    print(Fore.MAGENTA + f"  POST http://localhost:{port}/database/query")
    print(Fore.MAGENTA + f"  POST http://localhost:{port}/database/generate-query")
    print(Fore.MAGENTA + f"  POST http://localhost:{port}/database/report")
    print(Fore.MAGENTA + f"  GET  http://localhost:{port}/database/tables")
    print(Fore.MAGENTA + f"  GET  http://localhost:{port}/database/health\n")
    
    print(Fore.YELLOW + "Presiona Ctrl+C para detener el servidor\n")
    
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )


if __name__ == '__main__':
    main()
