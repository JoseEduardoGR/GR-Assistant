#!/bin/bash
# GR Assistant TUI
# Interactive Command Line Interface

# ==========================================
# CONFIGURACIÓN
# ==========================================
BASE_URL="http://160.34.211.247:8000"
CONFIG_FILE="$HOME/.gr_assistant"

# Colores ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
print_logo() {
    clear
    echo -e "${PURPLE}${BOLD}"
    cat << "EOF"
   ____ ____    _             _     _              _   
  / ___|  _ \  / \   ___ ___(_)___| |_ __ _ _ __ | |_ 
 | |  _| |_) |/ _ \ / __/ __| / __| __/ _` | '_ \| __|
 | |_| |  _ </ ___ \\__ \__ \ \__ \ || (_| | | | | |_ 
  \____|_| \_\_/   \_\___/___/_|___/\__\__,_|_| |_|\__|
EOF
    echo -e "${NC}"
    echo -e "   ✨ ${CYAN}Tu Asistente SaaS Impulsado por IA${NC} ✨"
    echo ""
}

print_success() {
    echo -e "${GREEN}✔ $1${NC}"
}

print_error() {
    echo -e "${RED}✖ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

save_config() {
    echo "API_KEY=$1" > "$CONFIG_FILE"
}

load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    fi
}

check_api_key() {
    load_config
    if [ -z "$API_KEY" ]; then
        print_error "No tienes una API Key configurada."
        print_info "Por favor, regístrate primero (Opción 1)."
        return 1
    fi
    return 0
}

pause() {
    echo ""
    read -p "Presiona ENTER para continuar..."
}

# ==========================================
# MÉTODOS DEL MENÚ
# ==========================================

menu_register() {
    echo -e "\n${BOLD}=== 1. Registro de Usuario ===${NC}"
    read -p "Tu Email: " email
    read -p "Tu Nombre/Empresa: " username
    
    if [ -z "$email" ] || [ -z "$username" ]; then
        print_error "El email y nombre no pueden estar vacíos."
        return
    fi
    
    echo -e "\nRegistrando..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"$email\", \"username\":\"$username\"}")
    
    SUCCESS=$(echo $RESPONSE | grep -o '"success":\s*true')
    
    if [ -n "$SUCCESS" ]; then
        API_KEY_EXTRACTED=$(echo $RESPONSE | grep -o '"api_key":\s*"[^"]*' | cut -d'"' -f4)
        save_config "$API_KEY_EXTRACTED"
        print_success "¡Registro Exitoso!"
        print_info "Tu API Key ha sido guardada automáticamente en tu computadora."
    else
        ERROR_MSG=$(echo $RESPONSE | grep -o '"error":\s*"[^"]*' | cut -d'"' -f4)
        print_error "Error: ${ERROR_MSG:-No se pudo conectar al servidor}"
    fi
}

menu_connect_db() {
    echo -e "\n${BOLD}=== 2. Conectar Base de Datos ===${NC}"
    check_api_key || return
    
    echo -e "Ingresa tu cadena de conexión (URI) de Postgres / Supabase."
    echo -e "${CYAN}Ejemplo: postgresql://postgres:pass@host:6543/postgres${NC}"
    read -p "URI: " db_uri
    
    if [ -z "$db_uri" ]; then
        print_error "La URI no puede estar vacía."
        return
    fi
    
    echo -e "\nConectando..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/client-db" \
      -H "Content-Type: application/json" \
      -H "x-api-key: $API_KEY" \
      -d "{\"connection_string\": \"$db_uri\"}")
      
    SUCCESS=$(echo $RESPONSE | grep -o '"success":\s*true')
    
    if [ -n "$SUCCESS" ]; then
        print_success "Base de Datos conectada y encriptada exitosamente."
    else
        ERROR_MSG=$(echo $RESPONSE | grep -o '"error":\s*"[^"]*' | cut -d'"' -f4)
        print_error "Error: ${ERROR_MSG:-Fallo en la conexión}"
    fi
}

menu_report() {
    echo -e "\n${BOLD}=== 3. Generar Reporte de Base de Datos ===${NC}"
    check_api_key || return
    
    echo -e "¿Qué reporte necesitas que extraiga la IA de tu base de datos?"
    echo -e "${CYAN}Ejemplo: 'Todos los alumnos, colores guinda, agrega logos'${NC}"
    read -p "Instrucción: " prompt
    
    if [ -z "$prompt" ]; then
        print_error "La instrucción no puede estar vacía."
        return
    fi
    
    echo -e "\n¿Formato del reporte?"
    echo "1) Word (.docx)"
    echo "2) Excel (.xlsx)"
    echo "3) PowerPoint (.pptx)"
    read -p "Elige (1/2/3): " form_op
    
    case $form_op in
        1) format="word"; ext="docx" ;;
        2) format="excel"; ext="xlsx" ;;
        3) format="powerpoint"; ext="pptx" ;;
        *) print_error "Opción no válida"; return ;;
    esac
    
    read -p "Nombre del archivo a guardar (sin extensión): " filename
    if [ -z "$filename" ]; then filename="Reporte"; fi
    
    echo -e "\n${YELLOW}Pensando y extrayendo datos (esto puede tomar de 10 a 30 segundos)...${NC}"
    
    # Realizar petición
    HTTP_CODE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/database/report" \
      -H "Content-Type: application/json" \
      -H "x-api-key: $API_KEY" \
      -d "{\"request\":\"$prompt\", \"report_type\":\"$format\"}" \
      -o "${filename}.${ext}")
      
    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "¡Reporte Generado con Éxito!"
        echo -e "Archivo guardado como: ${BOLD}${filename}.${ext}${NC} en la carpeta actual."
    else
        print_error "Ocurrió un error (Código: $HTTP_CODE)."
        cat "${filename}.${ext}" # Mostrará el error JSON en lugar del archivo
        rm "${filename}.${ext}" 2>/dev/null
    fi
}

menu_health() {
    echo -e "\n${BOLD}=== 4. Estado del Servidor ===${NC}"
    RESPONSE=$(curl -s -X GET "$BASE_URL/health")
    
    STATUS=$(echo $RESPONSE | grep -o '"status":\s*"[^"]*' | cut -d'"' -f4)
    MODEL=$(echo $RESPONSE | grep -o '"model":\s*"[^"]*' | cut -d'"' -f4)
    
    if [ "$STATUS" == "healthy" ]; then
        print_success "Servidor En Línea y Listo"
        echo -e "Modelo Activo: ${CYAN}$MODEL${NC}"
    else
        print_error "No se pudo conectar al servidor."
    fi
}

# ==========================================
# BUCLE PRINCIPAL
# ==========================================

while true; do
    print_logo
    
    load_config
    if [ -n "$API_KEY" ]; then
        echo -e "👤 Estado: ${GREEN}Conectado${NC} (API Key detectada)"
    else
        echo -e "👤 Estado: ${RED}No Registrado${NC}"
    fi
    
    echo -e "\n${BOLD}Menú Principal:${NC}"
    echo "  1) 🔑 Registrarse (Obtener API Key)"
    echo "  2) 🗄️  Conectar mi Base de Datos"
    echo "  3) 📄 Generar Reporte con IA"
    echo "  4) 🌐 Revisar Salud del Servidor"
    echo "  5) ❌ Salir"
    echo ""
    read -p "Elige una opción (1-5): " option

    case $option in
        1) menu_register ;;
        2) menu_connect_db ;;
        3) menu_report ;;
        4) menu_health ;;
        5) echo -e "${CYAN}¡Hasta pronto!${NC}"; break ;;
        *) print_error "Opción no válida." ;;
    esac
    pause
done
