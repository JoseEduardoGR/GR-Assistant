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
    echo -e "                   ${CYAN}v1.0.0${NC}"
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
    read -p "Presiona ENTER para continuar..." < /dev/tty
}

# ==========================================
# MÉTODOS DEL MENÚ
# ==========================================

menu_register() {
    echo -e "\n${BOLD}=== 1. Registro de Usuario ===${NC}"
    read -p "Tu Email: " email < /dev/tty
    read -p "Tu Nombre/Empresa: " username < /dev/tty
    
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
    read -p "URI: " db_uri < /dev/tty
    
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
    echo -e "\n${BOLD}=== 3. Generar Documento Mágico con IA ===${NC}"
    check_api_key || return
    
    echo -e "\n¿Qué necesitas que haga la IA? (Escribe lo que sea, la IA decidirá si necesita usar tu Base de Datos o inventarlo)"
    echo -e "${CYAN}Ejemplo 1: 'Crea una carta de bienvenida para la escuela TESCI'${NC}"
    echo -e "${CYAN}Ejemplo 2: 'Todos los alumnos con sus calificaciones, colores guinda'${NC}"
    read -p "Instrucción: " prompt < /dev/tty
    
    if [ -z "$prompt" ]; then
        print_error "La instrucción no puede estar vacía."
        return
    fi
    
    echo -e "\n¿Formato del documento?"
    echo "1) Word (.docx)"
    echo "2) Excel (.xlsx)"
    echo "3) PowerPoint (.pptx)"
    read -p "Elige (1/2/3): " form_op < /dev/tty
    
    case $form_op in
        1) format="word"; ext="docx" ;;
        2) format="excel"; ext="xlsx" ;;
        3) format="powerpoint"; ext="pptx" ;;
        *) print_error "Opción no válida"; return ;;
    esac
    
    read -p "Nombre del archivo a guardar (sin extensión): " filename < /dev/tty
    if [ -z "$filename" ]; then filename="Reporte"; fi
    
    echo -e "\n${YELLOW}La IA está enrutando tu solicitud, redactando y diseñando...${NC}"
    
    # Obtener modelo activo
    activeModel="IA"
    PREF_RESPONSE=$(curl -s -X GET "$BASE_URL/preferences" -H "x-api-key: $API_KEY")
    MODEL_MATCH=$(echo "$PREF_RESPONSE" | grep -o '"ai_model":\s*"[^"]*' | cut -d'"' -f4)
    if [ -n "$MODEL_MATCH" ]; then activeModel="$MODEL_MATCH"; fi
    
    # Realizar petición al Endpoint Universal en segundo plano para mostrar spinner
    curl -s -w "%{http_code}" -X POST "$BASE_URL/$ext" \
      -H "Content-Type: application/json" \
      -H "x-api-key: $API_KEY" \
      -d "{\"request\":\"$prompt\", \"download\":true, \"send_file\":true}" \
      -o "${filename}.${ext}" > "/tmp/gr_http_code_$$" &
      
    CURL_PID=$!
    spinner=( "⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏" )
    i=0
    while kill -0 $CURL_PID 2>/dev/null; do
        i=$(( (i+1) % 10 ))
        printf "\r${YELLOW}${spinner[$i]} Generando con $activeModel... (toma 10-30s)${NC}"
        sleep 0.1
    done
    wait $CURL_PID
    
    HTTP_CODE=$(cat "/tmp/gr_http_code_$$" 2>/dev/null)
    rm -f "/tmp/gr_http_code_$$"
    printf "\r\033[K" # Limpiar la línea del spinner
      
    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "¡Documento Generado con Éxito!"
        echo -e "Archivo guardado como: ${BOLD}${filename}.${ext}${NC} en la carpeta actual."
    else
        print_error "Ocurrió un error (Código: $HTTP_CODE)."
        cat "${filename}.${ext}" # Mostrará el error JSON en lugar del archivo
        rm "${filename}.${ext}" 2>/dev/null
    fi
}

menu_upload() {
    echo -e "\n${BOLD}=== 4. Subir un Archivo (Logo / Plantilla) ===${NC}"
    check_api_key || return
    
    echo -e "Ingresa la ruta absoluta o relativa del archivo en tu computadora."
    echo -e "${CYAN}Ejemplo: ./logo.png o /home/usuario/plantilla.xlsx${NC}"
    read -p "Ruta del archivo: " filepath < /dev/tty
    
    if [ ! -f "$filepath" ]; then
        print_error "El archivo no existe en esa ruta."
        return
    fi
    
    echo -e "\n¿Con qué nombre quieres que la IA conozca este archivo? (Opcional)"
    echo -e "${CYAN}Ejemplo: 'logo_empresa'${NC}"
    read -p "Nombre: " semantic_name < /dev/tty
    
    echo -e "\nSubiendo archivo..."
    
    if [ -z "$semantic_name" ]; then
        RESPONSE=$(curl -s -X POST "$BASE_URL/files" \
          -H "x-api-key: $API_KEY" \
          -F "file=@$filepath")
    else
        RESPONSE=$(curl -s -X POST "$BASE_URL/files" \
          -H "x-api-key: $API_KEY" \
          -F "file=@$filepath" \
          -F "name=$semantic_name")
    fi
    
    SUCCESS=$(echo $RESPONSE | grep -o '"success":\s*true')
    if [ -n "$SUCCESS" ]; then
        print_success "Archivo subido exitosamente."
    else
        ERROR_MSG=$(echo $RESPONSE | grep -o '"error":\s*"[^"]*' | cut -d'"' -f4)
        print_error "Error: ${ERROR_MSG:-No se pudo subir el archivo}"
    fi
}

menu_preferences() {
    echo -e "\n${BOLD}=== 5. Preferencias de IA y Estilo ===${NC}"
    check_api_key || return
    
    echo -e "Configura tu entorno. Deja en blanco los campos que no quieras cambiar."
    read -p "Nombre / Info de tu Empresa: " company_info < /dev/tty
    read -p "Estilo de Redacción (ej. 'Formal, alegre'): " prompt_style < /dev/tty
    echo -e "\n${CYAN}Si tienes tu propia API Key de OpenRouter, ingrésala aquí para usar modelos premium.${NC}"
    echo -e "Déjalo en blanco para usar la gratuita del servidor."
    read -p "OpenRouter API Key (Opcional): " openrouter_key < /dev/tty
    
    echo -e "\n${CYAN}Obteniendo modelos disponibles...${NC}"
    ai_model=""
    
    MODELS_RESP=$(curl -s "$BASE_URL/models")
    RECOMMENDED=$(echo "$MODELS_RESP" | grep -o '"recommended":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$MODELS_RESP" ] && echo "$MODELS_RESP" | grep -q '"success":true'; then
        # Extraer la lista de modelos del JSON
        MODEL_LIST=$(echo "$MODELS_RESP" | grep -o '"models":\[[^]]*\]' | sed 's/"models":\[//;s/\]//' | tr ',' '\n' | tr -d '"')
        
        echo -e "\n${CYAN}Modelos disponibles (actualizados en tiempo real):${NC}"
        idx=1
        declare -a MODEL_ARRAY
        while IFS= read -r model_id; do
            model_id=$(echo "$model_id" | xargs)  # trim
            [ -z "$model_id" ] && continue
            MODEL_ARRAY[$idx]="$model_id"
            LABEL=""
            [ "$model_id" = "$RECOMMENDED" ] && LABEL=" ⭐ (Recomendado)"
            echo "${idx}) ${model_id}${LABEL}"
            idx=$((idx + 1))
        done <<< "$MODEL_LIST"
        
        SKIP_OP=$idx
        echo "${SKIP_OP}) No cambiar modelo"
        read -p "Elige (1-${SKIP_OP}): " model_op < /dev/tty
        
        if [ "$model_op" -ge 1 ] && [ "$model_op" -lt "$SKIP_OP" ] 2>/dev/null; then
            ai_model="${MODEL_ARRAY[$model_op]}"
        fi
    else
        echo -e "${YELLOW}No se pudo obtener la lista de modelos. Usando lista de emergencia.${NC}"
        echo "1) cohere/north-mini-code:free (Recomendado)"
        echo "2) meta-llama/llama-3.3-70b-instruct:free"
        echo "3) qwen/qwen-2.5-72b-instruct:free"
        echo "4) anthropic/claude-3.5-haiku (Requiere API Key propia)"
        echo "5) No cambiar modelo"
        read -p "Elige (1-5): " model_op < /dev/tty
        case $model_op in
            1) ai_model="cohere/north-mini-code:free" ;;
            2) ai_model="meta-llama/llama-3.3-70b-instruct:free" ;;
            3) ai_model="qwen/qwen-2.5-72b-instruct:free" ;;
            4) ai_model="anthropic/claude-3.5-haiku" ;;
        esac
    fi
    
    # Construir el JSON manualmente para evitar jq (no siempre instalado)
    json="{"
    [ -n "$company_info" ] && json="$json\"company_info\":\"$company_info\","
    [ -n "$prompt_style" ] && json="$json\"prompt_style\":\"$prompt_style\","
    [ -n "$ai_model" ] && json="$json\"ai_model\":\"$ai_model\","
    [ -n "$openrouter_key" ] && json="$json\"openrouter_key\":\"$openrouter_key\","
    json="${json%,}" # Quitar última coma
    json="$json}"
    
    if [ "$json" = "{}" ]; then
        print_info "No se hicieron cambios."
        return
    fi
    
    echo -e "\nActualizando..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/preferences" \
      -H "Content-Type: application/json" \
      -H "x-api-key: $API_KEY" \
      -d "$json")
      
    SUCCESS=$(echo $RESPONSE | grep -o '"success":\s*true')
    if [ -n "$SUCCESS" ]; then
        print_success "Preferencias guardadas exitosamente."
    else
        ERROR_MSG=$(echo $RESPONSE | grep -o '"error":\s*"[^"]*' | cut -d'"' -f4)
        print_error "Error: ${ERROR_MSG:-No se pudo actualizar}"
    fi
}

menu_health() {
    echo -e "\n${BOLD}=== 6. Estado del Servidor ===${NC}"
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
    echo "  3) 📄 Generar Documento / Reporte con IA"
    echo "  4) 🖼️  Subir Archivo (Logo / Plantilla)"
    echo "  5) ⚙️  Preferencias de IA y Estilo"
    echo "  6) 🌐 Revisar Salud del Servidor"
    echo "  7) ❌ Salir"
    echo ""
    read -p "Elige una opción (1-7): " option < /dev/tty

    case $option in
        1) menu_register ;;
        2) menu_connect_db ;;
        3) menu_report ;;
        4) menu_upload ;;
        5) menu_preferences ;;
        6) menu_health ;;
        7) echo -e "${CYAN}¡Hasta pronto!${NC}"; break ;;
        *) print_error "Opción no válida." ;;
    esac
    pause
done
