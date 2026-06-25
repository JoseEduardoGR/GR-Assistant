# GR Assistant TUI for Windows
$ErrorActionPreference = "Stop"

$BASE_URL = "http://160.34.211.247:8000"
$CONFIG_FILE = "$env:USERPROFILE\.gr_assistant"

function Print-Logo {
    Clear-Host
    Write-Host "   ____ ____    _             _     _              _   " -ForegroundColor Magenta
    Write-Host "  / ___|  _ \  / \   ___ ___(_)___| |_ __ _ _ __ | |_ " -ForegroundColor Magenta
    Write-Host " | |  _| |_) |/ _ \ / __/ __| / __| __/ _`` | '_ \| __|" -ForegroundColor Magenta
    Write-Host " | |_| |  _ </ ___ \\__ \__ \ \__ \ || (_| | | | | |_ " -ForegroundColor Magenta
    Write-Host "  \____|_| \_\_/   \_\___/___/_|___/\__\__,_|_| |_|\__|" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "                   v1.0.0" -ForegroundColor Cyan
    Write-Host ""
}

function Print-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Print-Error($msg) { Write-Host "[ERR] $msg" -ForegroundColor Red }
function Print-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Yellow }

function Save-Config($key) {
    "API_KEY=$key" | Out-File -FilePath $CONFIG_FILE -Encoding UTF8
}

function Load-Config {
    if (Test-Path $CONFIG_FILE) {
        $content = Get-Content $CONFIG_FILE
        if ($content -match "^API_KEY=(.*)$") {
            return $matches[1]
        }
    }
    return $null
}

function Check-ApiKey {
    $key = Load-Config
    if ([string]::IsNullOrEmpty($key)) {
        Print-Error "No tienes una API Key configurada."
        Print-Info "Por favor, regístrate primero (Opción 1)."
        return $null
    }
    return $key
}

function Pause-Script {
    Write-Host ""
    Read-Host "Presiona ENTER para continuar..."
}

function Menu-Register {
    Write-Host "`n=== 1. Registro de Usuario ===" -ForegroundColor White
    $email = Read-Host "Tu Email"
    $username = Read-Host "Tu Nombre/Empresa"
    
    if ([string]::IsNullOrWhiteSpace($email) -or [string]::IsNullOrWhiteSpace($username)) {
        Print-Error "El email y nombre no pueden estar vacíos."
        return
    }
    
    Write-Host "`nRegistrando..."
    $body = @{ email = $email; username = $username } | ConvertTo-Json
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/register" -Method Post -Body $body -ContentType "application/json"
        if ($response.success) {
            Save-Config $response.api_key
            Print-Success "¡Registro Exitoso!"
            Print-Info "Tu API Key ha sido guardada automáticamente en tu computadora."
        } else {
            Print-Error "Error: $($response.error)"
        }
    } catch {
        Print-Error "Error al conectar con el servidor."
    }
}

function Menu-ConnectDB {
    Write-Host "`n=== 2. Conectar Base de Datos ===" -ForegroundColor White
    $apiKey = Check-ApiKey
    if (-not $apiKey) { return }
    
    Write-Host "Ingresa tu cadena de conexión (URI) de Postgres / Supabase."
    Write-Host "Ejemplo: postgresql://postgres:pass@host:6543/postgres" -ForegroundColor Cyan
    $db_uri = Read-Host "URI"
    
    if ([string]::IsNullOrWhiteSpace($db_uri)) {
        Print-Error "La URI no puede estar vacía."
        return
    }
    
    Write-Host "`nConectando..."
    $body = @{ connection_string = $db_uri } | ConvertTo-Json
    $headers = @{ "x-api-key" = $apiKey }
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/client-db" -Method Post -Headers $headers -Body $body -ContentType "application/json"
        if ($response.success) {
            Print-Success "Base de Datos conectada y encriptada exitosamente."
        } else {
            Print-Error "Error: $($response.error)"
        }
    } catch {
        $errMsg = $_.Exception.Message
        try {
            $errBody = $_.ErrorDetails.Message | ConvertFrom-Json
            $errMsg = $errBody.error
        } catch {}
        Print-Error "Error: $errMsg"
    }
}

function Menu-Report {
    Write-Host "`n=== 3. Generar Documento Mágico con IA ===" -ForegroundColor White
    $apiKey = Check-ApiKey
    if (-not $apiKey) { return }
    
    Write-Host "`n¿Qué necesitas que haga la IA? (Escribe lo que sea, la IA decidirá si necesita usar tu Base de Datos o inventarlo)"
    Write-Host "Ejemplo 1: 'Crea una carta de bienvenida para la escuela TESCI'" -ForegroundColor Cyan
    Write-Host "Ejemplo 2: 'Todos los alumnos con sus calificaciones, colores guinda'" -ForegroundColor Cyan
    $prompt = Read-Host "Instrucción"
    
    if ([string]::IsNullOrWhiteSpace($prompt)) {
        Print-Error "La instrucción no puede estar vacía."
        return
    }
    
    Write-Host "`n¿Formato del documento?"
    Write-Host "1) Word (.docx)"
    Write-Host "2) Excel (.xlsx)"
    Write-Host "3) PowerPoint (.pptx)"
    $form_op = Read-Host "Elige (1/2/3)"
    
    $ext = ""
    switch ($form_op) {
        "1" { $ext = "docx" }
        "2" { $ext = "xlsx" }
        "3" { $ext = "pptx" }
        default { Print-Error "Opción no válida"; return }
    }
    
    $filename = Read-Host "Nombre del archivo a guardar (sin extensión)"
    if ([string]::IsNullOrWhiteSpace($filename)) { $filename = "Reporte" }
    
    Write-Host "`nLa IA está enrutando tu solicitud, redactando y diseñando..." -ForegroundColor Yellow
    
    $body = @{ request = $prompt; download = $true; send_file = $true } | ConvertTo-Json
    $headers = @{ "x-api-key" = $apiKey }
    $outFile = "$PWD\$filename.$ext"
    
    $activeModel = "IA"
    try {
        $prefResponse = Invoke-RestMethod -Uri "$BASE_URL/preferences" -Method Get -Headers $headers
        if ($prefResponse.success -and $prefResponse.preferences.ai_model) {
            $activeModel = $prefResponse.preferences.ai_model
        }
    } catch {}
    
    $job = Start-Job -ScriptBlock {
        param($baseUrl, $ext, $headers, $body, $outFile)
        try {
            Invoke-RestMethod -Uri "$baseUrl/$ext" -Method Post -Headers $headers -Body $body -ContentType "application/json" -OutFile $outFile
            return @{ success = $true }
        } catch {
            return @{ success = $false; error = $_.Exception.Message }
        }
    } -ArgumentList $BASE_URL, $ext, $headers, $body, $outFile
    
    $spinner = @("|", "/", "-", "\")
    $i = 0
    while ($job.State -eq "Running") {
        Write-Host -NoNewline "`r[$($spinner[$i])] Generando con $activeModel... (toma 10-30s)" -ForegroundColor Yellow
        $i = ($i + 1) % 4
        Start-Sleep -Milliseconds 150
    }
    Write-Host "`r                                                                 `r" -NoNewline
    
    $result = Receive-Job -Job $job
    Remove-Job -Job $job
    
    if ($result.success) {
        Print-Success "¡Documento Generado con Éxito!"
        Write-Host "Archivo guardado como: $filename.$ext en la carpeta actual."
    } else {
        Print-Error "Ocurrió un error."
        Write-Host $result.error -ForegroundColor Red
    }
}

function Menu-Upload {
    Write-Host "`n=== 4. Subir un Archivo (Logo / Plantilla) ===" -ForegroundColor White
    $apiKey = Check-ApiKey
    if (-not $apiKey) { return }
    
    Write-Host "Ingresa la ruta absoluta o relativa del archivo en tu computadora."
    Write-Host "Ejemplo: .\logo.png o C:\usuario\plantilla.xlsx" -ForegroundColor Cyan
    $filepath = Read-Host "Ruta del archivo"
    
    if (-not (Test-Path $filepath)) {
        Print-Error "El archivo no existe en esa ruta."
        return
    }
    
    Write-Host "`n¿Con qué nombre quieres que la IA conozca este archivo? (Opcional)"
    Write-Host "Ejemplo: 'logo_empresa'" -ForegroundColor Cyan
    $semantic_name = Read-Host "Nombre"
    
    Write-Host "`nSubiendo archivo..."
    
    try {
        # Usamos curl.exe nativo de Windows 10 para evitar problemas con multipart/form-data en PS 5.1
        $curlPath = "curl.exe"
        if ([string]::IsNullOrWhiteSpace($semantic_name)) {
            $out = & $curlPath -s -X POST "$BASE_URL/files" -H "x-api-key: $apiKey" -F "file=@$filepath"
        } else {
            $out = & $curlPath -s -X POST "$BASE_URL/files" -H "x-api-key: $apiKey" -F "file=@$filepath" -F "name=$semantic_name"
        }
        
        $response = $out | ConvertFrom-Json
        if ($response.success) {
            Print-Success "Archivo subido exitosamente."
        } else {
            Print-Error "Error: $($response.error)"
        }
    } catch {
        Print-Error "No se pudo subir el archivo."
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

function Menu-Preferences {
    Write-Host "`n=== 5. Preferencias de IA y Estilo ===" -ForegroundColor White
    $apiKey = Check-ApiKey
    if (-not $apiKey) { return }
    
    Write-Host "Configura tu entorno. Deja en blanco los campos que no quieras cambiar."
    $company_info = Read-Host "Nombre / Info de tu Empresa"
    $prompt_style = Read-Host "Estilo de Redacción (ej. 'Formal, alegre')"
    Write-Host "`nSi tienes tu propia API Key de OpenRouter, ingrésala aquí para usar modelos premium." -ForegroundColor Cyan
    Write-Host "Déjalo en blanco para usar la gratuita del servidor."
    $openrouter_key = Read-Host "OpenRouter API Key (Opcional)"
    
    Write-Host "`nObteniendo modelos disponibles..." -ForegroundColor Cyan
    $ai_model = ""
    try {
        $modelsResp = Invoke-RestMethod -Uri "$BASE_URL/models" -Method Get
        $modelList = $modelsResp.models
        $recommended = $modelsResp.recommended
        
        Write-Host "`nModelos disponibles (actualizados en tiempo real):" -ForegroundColor Cyan
        for ($idx = 0; $idx -lt $modelList.Count; $idx++) {
            $m = $modelList[$idx]
            $label = if ($m -eq $recommended) { " ⭐ (Recomendado)" } else { "" }
            $isPaid = if ($m -notmatch ":free") { " (Requiere API Key propia)" } else { "" }
            Write-Host "$($idx+1)) $m$label$isPaid"
        }
        $skipOp = $modelList.Count + 1
        Write-Host "$skipOp) No cambiar modelo"
        
        $model_op = Read-Host "Elige (1-$skipOp)"
        $modelIdx = [int]$model_op - 1
        if ($modelIdx -ge 0 -and $modelIdx -lt $modelList.Count) {
            $ai_model = $modelList[$modelIdx]
        }
    } catch {
        Write-Host "No se pudo obtener la lista de modelos. Usando lista de emergencia." -ForegroundColor Yellow
        Write-Host "1) cohere/north-mini-code:free (Recomendado)"
        Write-Host "2) meta-llama/llama-3.3-70b-instruct:free"
        Write-Host "3) qwen/qwen-2.5-72b-instruct:free"
        Write-Host "4) anthropic/claude-3.5-haiku (Requiere API Key propia)"
        Write-Host "5) No cambiar modelo"
        $model_op = Read-Host "Elige (1-5)"
        switch ($model_op) {
            "1" { $ai_model = "cohere/north-mini-code:free" }
            "2" { $ai_model = "meta-llama/llama-3.3-70b-instruct:free" }
            "3" { $ai_model = "qwen/qwen-2.5-72b-instruct:free" }
            "4" { $ai_model = "anthropic/claude-3.5-haiku" }
        }
    }
    
    $prefObj = @{}
    if (-not [string]::IsNullOrWhiteSpace($company_info)) { $prefObj.Add("company_info", $company_info) }
    if (-not [string]::IsNullOrWhiteSpace($prompt_style)) { $prefObj.Add("prompt_style", $prompt_style) }
    if (-not [string]::IsNullOrWhiteSpace($ai_model)) { $prefObj.Add("ai_model", $ai_model) }
    if (-not [string]::IsNullOrWhiteSpace($openrouter_key)) { $prefObj.Add("openrouter_key", $openrouter_key) }
    
    if ($prefObj.Count -eq 0) {
        Print-Info "No se hicieron cambios."
        return
    }
    
    Write-Host "`nActualizando..."
    $body = $prefObj | ConvertTo-Json
    $headers = @{ "x-api-key" = $apiKey }
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/preferences" -Method Post -Headers $headers -Body $body -ContentType "application/json"
        if ($response.success) {
            Print-Success "Preferencias guardadas exitosamente."
        } else {
            Print-Error "Error: $($response.error)"
        }
    } catch {
        Print-Error "No se pudo actualizar."
    }
}

function Menu-Health {
    Write-Host "`n=== 6. Estado del Servidor ===" -ForegroundColor White
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
        if ($response.status -eq "healthy") {
            Print-Success "Servidor En Línea y Listo"
            Write-Host "Modelo Activo: $($response.model)" -ForegroundColor Cyan
        } else {
            Print-Error "No se pudo conectar al servidor."
        }
    } catch {
        Print-Error "No se pudo conectar al servidor."
    }
}

# MAIN LOOP
while ($true) {
    Print-Logo
    $apiKey = Load-Config
    
    if (-not [string]::IsNullOrEmpty($apiKey)) {
        Write-Host -NoNewline "[User] Estado: "
        Write-Host -NoNewline "Conectado" -ForegroundColor Green
        Write-Host " (API Key detectada)"
    } else {
        Write-Host -NoNewline "[User] Estado: "
        Write-Host "No Registrado" -ForegroundColor Red
    }
    
    Write-Host "`nMenú Principal:" -ForegroundColor White
    Write-Host "  1) [KEY] Registrarse (Obtener API Key)"
    Write-Host "  2) [DB]  Conectar mi Base de Datos"
    Write-Host "  3) [DOC] Generar Documento / Reporte con IA"
    Write-Host "  4) [IMG] Subir Archivo (Logo / Plantilla)"
    Write-Host "  5) [CFG] Preferencias de IA y Estilo"
    Write-Host "  6) [WEB] Revisar Salud del Servidor"
    Write-Host "  7) [X]   Salir`n"
    
    $option = Read-Host "Elige una opción (1-7)"
    
    switch ($option) {
        "1" { Menu-Register }
        "2" { Menu-ConnectDB }
        "3" { Menu-Report }
        "4" { Menu-Upload }
        "5" { Menu-Preferences }
        "6" { Menu-Health }
        "7" { Write-Host "¡Hasta pronto!" -ForegroundColor Cyan; break }
        default { Print-Error "Opción no válida." }
    }
    if ($option -eq "7") { break }
    Pause-Script
}
