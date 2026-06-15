<table>
<tr>
<td width="150">
<img src="assets/GRDocs.jpg" width="100%" style="display:block;">
</td>
<td>
<h1>GR Assistant</h1>
<em>"Tu Asistente SaaS Impulsado por IA para Análisis de Bases de Datos y Documentos"</em>
</td>
</tr>
</table>

![Banner](https://img.shields.io/badge/GR_Assistant-v1.0.0-blueviolet?style=for-the-badge&logo=python)
![Powered by Python](https://img.shields.io/badge/Powered%20by-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Powered by Node.js](https://img.shields.io/badge/Powered%20by-Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)
![AI Powered](https://img.shields.io/badge/AI-Powered-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)

---

## 📋 Tabla de Contenidos

- [Sobre GR Assistant](#-sobre-gr-docs)
- [Características](#-características-destacadas)
- [Flujo de Trabajo](#-flujo-de-trabajo)
- [Instalación](#️-instalación-y-configuración)
- [Uso](#-cómo-usar-gr-docs)
- [Modelos Disponibles](#-modelos-de-ia-disponibles)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Solución de Problemas](#-solución-de-problemas)
- [Licencia](#-licencia)

---

## 💡 Sobre GR Assistant

**GR Assistant** es un **generador de documentos profesionales** que utiliza **Inteligencia Artificial** para crear archivos **Word**, **Excel**, **PowerPoint** y **PDF** de forma automática.

> [!NOTE]
> GR Assistant utiliza modelos de IA avanzados para generar código que crea documentos profesionales. No es un simple template, ¡es un generador inteligente!

Gracias a **Llama, Gemini, Qwen y otros modelos de IA**, puedes:

* 📝 Generar **documentos Word** con formato profesional usando `docx`
* 📊 Crear **hojas de cálculo Excel** con fórmulas y gráficos usando `openpyxl`
* 🎨 Diseñar **presentaciones PowerPoint** con layouts variados usando `pptxgenjs`
* 🤖 Personalizar el **contenido y estilo** mediante lenguaje natural
* ⚡ Ejecutar todo desde la **línea de comandos** o **API REST**

> [!TIP]
> GR Assistant es una API REST diseñada para integrarse fácilmente como un microservicio (SaaS) en tus aplicaciones web o móviles.
> Ya no cuenta con modo interactivo de terminal, enfocándose 100% en rendimiento y escalabilidad.

---

## 🔄 Flujo de Trabajo

```mermaid
graph TD
    A[👤 Usuario] -->|Describe Documento| B(🤖 GR Assistant)
    B -->|Selecciona Modelo IA| C{🧠 Llama/Gemini/Qwen}
    C -->|Genera Script| D[📜 Script JS/Python]
    D -->|Ejecuta| E[⚙️ Librería docx/openpyxl/pptxgenjs]
    E -->|Crea| F[📄 Documento Final]
    F -->|Descarga| A
    
    style B fill:#8A2BE2,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#4285F4,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#43A047,stroke:#333,stroke-width:2px,color:#fff
```

---

## ✨ Características Destacadas

| ⚡ Funcionalidad | 📌 Detalle |
| --- | --- |
| **Generación Inteligente** | Describe lo que necesitas y la IA genera el código automáticamente |
| **Multi-formato** | Word (.docx), Excel (.xlsx), PowerPoint (.pptx) |
| **Base de Datos SQL Server** | Consultas inteligentes y reportes automáticos desde tu base de datos |
| **Personalización Total** | Colores, estilos, tablas, gráficos, todo configurable |
| **API REST Exclusiva** | Integración transparente con frontends web o móviles |
| **Multitenancy y SaaS** | Sistema de API Keys para soportar múltiples clientes de forma segura |
| **Actualización Automática** | Webhook integrado para despliegue continuo desde GitHub |
| **Múltiples Modelos IA** | Llama, Gemini, Qwen, DeepSeek, Mistral y más vía OpenRouter |
| **Manejo de Errores IA** | Auto-corrección inteligente de hasta 5 intentos si el script falla |

> [!IMPORTANT]
> GR Assistant requiere una API key de OpenRouter para funcionar. Hay muchos modelos completamente gratuitos disponibles.

---

## 🎨 Badges & Estado

![Python](https://img.shields.io/badge/Python-3.8+-brightgreen?style=for-the-badge&logo=python)
![Node.js](https://img.shields.io/badge/Node.js-Required-green?style=for-the-badge&logo=node.js)
![Status](https://img.shields.io/badge/Status-Production-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-Custom-orange?style=for-the-badge)

---

## ⚙️ Instalación y Configuración

> [!WARNING]
> Asegúrate de tener Python 3.8+ y Node.js 14+ instalados antes de continuar.

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/grcodedigitalsolutions/GR_Docs.git
cd GR_Docs
```

### 2️⃣ Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3️⃣ Instalar Dependencias Python

```bash
pip install -r requirements.txt
```

> [!NOTE]
> Si no existe `requirements.txt`, instala manualmente:
> ```bash
> pip install pyyaml colorama requests openpyxl
> ```

### 4️⃣ Instalar Dependencias Node.js

```bash
npm install
```

Esto instalará:
- `docx` - Para generar documentos Word
- `pptxgenjs` - Para generar presentaciones PowerPoint

---

### 5️⃣ Configurar la API Key y Credenciales

Para que **GR Assistant** funcione necesitas:
1. Una **API key de OpenRouter** (para la IA)
2. **Credenciales de SQL Server** (opcional, solo si usarás el módulo de base de datos)

| Servicio | Badge | Pasos para generar la API |
| --- | --- | --- |
| **OpenRouter** | <img src="https://openrouter.ai/favicon.ico" alt="OpenRouter" width="32"/> | 1. Ve a [OpenRouter Keys](https://openrouter.ai/settings/keys)<br>2. Inicia sesión o crea una cuenta<br>3. Genera tu API key<br>4. **Hay modelos gratuitos disponibles** sin necesidad de pago |

> [!TIP]
> OpenRouter te da acceso a múltiples modelos de IA (Claude, Gemini, Llama, etc.) con una sola API key. Muchos modelos son completamente gratuitos.

#### 📝 Crear el archivo `.env`

**Opción 1: Copiar desde plantilla**

```bash
cp .env.example .env
```

Luego edita `.env` con tus credenciales:

```env
# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-tu-api-key-aqui

# SQL Server Database Credentials (opcional)
DB_SERVER=127.0.0.1,1433
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=nombre_base_datos_opcional
DB_DRIVER=ODBC Driver 17 for SQL Server
```

**Opción 2: Crear manualmente**

```bash
# Con nano
nano .env

# Con vim
vim .env

# Con VS Code
code .env
```

#### ✅ Verificar la Configuración

```bash
# Verificar que el archivo existe
ls -la .env

# Ver los primeros caracteres (sin mostrar la key completa)
head -c 20 .env && echo "..."
```

**Salida esperada:**
```
sk-or-v1-1234567890...
```

> [!CAUTION]
> **NUNCA** compartas tu API key ni la subas a GitHub. El archivo `.env` ya está en `.gitignore`.

---

## 🧠 Modelos de IA Disponibles

Los usuarios de la API pueden configurar su modelo preferido a través del endpoint `/preferences` enviando el campo `ai_model`. 
Actualmente, los siguientes 5 modelos gratuitos de alto rendimiento están permitidos:

1. `meta-llama/llama-3.3-70b-instruct:free` (Llama 3.3)
2. `google/gemini-2.0-flash-exp:free` (Gemini 2.0)
3. `qwen/qwen-2.5-72b-instruct:free` (Qwen 2.5)
4. `deepseek/deepseek-chat:free` (DeepSeek V3)
5. `mistralai/mistral-nemo:free` (Mistral)

> [!TIP]
> Llama 3.3 70B y Gemini 2.0 Flash son los recomendados por defecto por su gran calidad de generación.

### 🔧 Configurar Modelo Global (Fallback)

Edita `settings.yaml` para cambiar el modelo que usarán los usuarios que no hayan especificado ninguno:

```yaml
# AI model default
model: qwen/qwen-2.5-72b-instruct:free
```

> [!NOTE]
> Puedes usar cualquier modelo disponible en OpenRouter. Los modelos con `:free` al final son completamente gratuitos.

Para ver todos los modelos gratuitos disponibles:

```bash
python list_models.py
```

---

## 🚀 Cómo Usar la API de GR Assistant

### 🌐 Iniciar el Servidor

```bash
python main.py
```

Esto iniciará un servidor FastAPI/Flask en `http://localhost:8000` (el modo de terminal ha sido depreciado).

> [!NOTE]
> El modo API permite integrar GR Assistant en tus aplicaciones. Ver [API_EXAMPLES.md](API_EXAMPLES.md) para documentación completa.

**Endpoints disponibles:**
- `GET /` - Información de la API
- `GET /health` - Estado del servidor
- `POST /docx` - Generar documento Word
- `POST /xlsx` - Generar archivo Excel
- `POST /pptx` - Generar presentación PowerPoint
- `POST /database/query` - Ejecutar consulta SQL
- `POST /database/generate-query` - Generar consulta con IA
- `POST /database/report` - Generar reporte desde base de datos
- `GET /database/tables` - Listar tablas de la base de datos
- `POST /preferences` - Subir/descargar preferencias de usuario (ej. `{"ai_model": "mistralai/mistral-nemo:free"}`)
- **`POST /files`** - (SaaS) Subir logos, encabezados y plantillas (soporta el campo `name` para etiquetas semánticas)
- **`POST /client-db`** - (SaaS) Configurar conexión segura a BD de clientes
- **`POST /webhook/github`** - Webhook para auto-actualizar el servidor (`git pull`)

> [!WARNING]
> Todos los endpoints requieren que envíes el header `x-api-key: TU_API_KEY`.

**Ejemplo rápido (Texto libre):**
```bash
curl -X POST http://localhost:8000/docx \
  -H "Content-Type: application/json" \
  -H "x-api-key: grdocs_test_key_123" \
  -d '{"request":"Informe de ventas Q1 2024","download":true}' \
  --output informe.docx
```

---

## 🚀 Guía Paso a Paso (Modo SaaS y Bases de Datos)

El flujo ideal para utilizar GR Assistant con conexión a bases de datos y personalización corporativa es el siguiente:

### 1️⃣ Obtener una API Key (Registro)

Regístrate para obtener tu llave maestra. Guárdala muy bien, no volverá a mostrarse.

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"tu@email.com", "username":"TuNombre"}'
```

### 2️⃣ Conectar tu Base de Datos (Supabase / Postgres / SQL Server)

Vincula tu base de datos con tu API Key. GR Assistant encriptará esta conexión por seguridad. *(Nota: Si usas Supabase en IPv4, asegúrate de usar el Session Pooler en el puerto `6543` o `5432` según asigne Supabase, y codifica tu contraseña con `%24` si usas signos de dólar).*

```bash
curl -X POST http://localhost:8000/client-db \
  -H "Content-Type: application/json" \
  -H "x-api-key: TU_API_KEY_AQUI" \
  -d '{"connection_string": "postgresql://postgres:tu_password@host:puerto/postgres"}'
```

### 3️⃣ Guardar tus Imágenes y Logos Corporativos (Opcional)

Sube las imágenes que la IA usará para adornar tus documentos. Asígnales nombres descriptivos.

```bash
curl -X POST http://localhost:8000/files \
  -H "x-api-key: TU_API_KEY_AQUI" \
  -F "file=@ruta/a/tu/logo_empresa.png" \
  -F "semantic_name=logo_oficial.png" \
  -F "description=Logo corporativo principal"
```

### 4️⃣ Generar Reportes Inteligentes desde la Base de Datos

¡Pide tu reporte! La IA extraerá los datos, aplicará el diseño que pidas e incrustará tus logos.

```bash
curl -X POST http://localhost:8000/database/report \
  -H "Content-Type: application/json" \
  -H "x-api-key: TU_API_KEY_AQUI" \
  -d '{"request":"Genera un reporte de todos los alumnos, pon encabezados color guinda e inserta el logo oficial", "report_type":"word"}' \
  --output "Reporte_Magico.docx"
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Generar Documento Word

```bash
curl -X POST http://localhost:8000/docx \
  -H "Content-Type: application/json" \
  -H "x-api-key: grdocs_test_key_123" \
  -d '{"request":"Informe de ventas Q1 2024 con tablas y gráficos","download":true}'
```

**Resultado:** `GR_Docs/doc/cache/output/informe-ventas-q1-2024.docx`

### Ejemplo 2: Generar Excel

```bash
curl -X POST http://localhost:8000/xlsx \
  -H "Content-Type: application/json" \
  -H "x-api-key: grdocs_test_key_123" \
  -d '{"request":"Control de inventario con fórmulas y formato condicional","download":true}'
```

**Resultado:** `GR_Docs/xlsx/cache/output/control-inventario.xlsx`

### Ejemplo 3: Generar PowerPoint

```bash
curl -X POST http://localhost:8000/pptx \
  -H "Content-Type: application/json" \
  -H "x-api-key: grdocs_test_key_123" \
  -d '{"request":"Presentación sobre Historia del Violín con 12 slides","download":true}'
```

**Resultado:** `GR_Docs/pptx/cache/output/historia-violin.pptx`

### Ejemplo 4: Consultar Base de Datos con IA

```bash
curl -X POST http://localhost:8000/database/generate-query \
  -H "Content-Type: application/json" \
  -H "x-api-key: grdocs_test_key_123" \
  -d '{"request":"muéstrame los últimos 10 registros de ventas","database":"mi_base_datos"}'
```

**Resultado:** Consulta SQL generada automáticamente

### Ejemplo 5: Generar Reporte desde Base de Datos

```bash
curl -X POST http://localhost:8000/database/report \
  -H "Content-Type: application/json" \
  -H "x-api-key: grdocs_test_key_123" \
  -d '{"request":"ventas del último mes agrupadas por producto","report_type":"excel","database":"mi_base_datos"}' \
  --output reporte-ventas.xlsx
```

**Resultado:** Archivo Excel con datos de la base de datos

### Ejemplo 6: Subir Imágenes y Recursos Gráficos Automáticos

Sube un archivo asignándole un "nombre semántico" (ej. encabezado, logo). La IA lo usará automáticamente en los siguientes documentos que generes:

```bash
curl -X POST http://localhost:8000/files \
  -H "x-api-key: grdocs_test_key_123" \
  -F "file=@/ruta/a/tu/encabezado.png" \
  -F "name=encabezado"
```

> [!NOTE]
> Para usar el módulo de base de datos, consulta [GR_DataBase/README.md](GR_DataBase/README.md)

## 📊 Monitoreo de Usuarios

Puedes visualizar en tiempo real todos los usuarios de la plataforma y el modelo de IA que están usando mediante el script de monitoreo (se conecta a la BD local):

```bash
python monitor.py
```

---

## 📂 Estructura del Proyecto

```text
GR_DOCS/
├─ assets/              # Recursos (logo, imágenes, engine IA)
│  ├─ GRDocs.jpg       # Logo del proyecto
│  ├─ context.gr       # Contexto para la IA
│  ├─ engine.py        # Motor de generación de IA
│  └─ openrouter.py    # Cliente de OpenRouter
├─ GR_DataBase/         # Módulo de base de datos SQL Server
│  ├─ __init__.py      # Inicialización del módulo
│  ├─ connection.py    # Conexión a SQL Server
│  ├─ queries.py       # Generación de consultas con IA
│  ├─ blueprints.py    # Endpoints de Flask para DB
│  ├─ context.gr       # Prompt para generación de SQL
│  ├─ example.py       # Ejemplos de uso
│  └─ README.md        # Documentación del módulo
├─ GR_Docs/             # Paquete principal de la aplicación
│  ├─ __init__.py      # Inicialización del paquete
│  ├─ blueprints.py    # Blueprints de Flask (rutas API)
│  ├─ server.py        # Servidor Flask
│  ├─ doc/             # Generador de Word
│  │  ├─ cache/        # Scripts y outputs generados
│  │  │  ├─ *.mjs      # Scripts JavaScript generados
│  │  │  └─ output/    # Documentos .docx finales
│  │  ├─ prompt.gr     # Prompt para generación de Word
│  │  └─ word.py       # Clase WordScriptGenerator
│  ├─ xlsx/            # Generador de Excel
│  │  ├─ cache/        # Scripts y outputs generados
│  │  │  ├─ *.py       # Scripts Python generados
│  │  │  └─ output/    # Archivos .xlsx finales
│  │  ├─ prompt.gr     # Prompt para generación de Excel
│  │  └─ excel.py      # Clase ExcelScriptGenerator
│  └─ pptx/            # Generador de PowerPoint
│     ├─ cache/        # Scripts y outputs generados
│     │  ├─ *.cjs      # Scripts CommonJS generados
│     │  └─ output/    # Presentaciones .pptx finales
│     ├─ prompt.gr     # Prompt para generación de PowerPoint
│     └─ powerpoint.py # Clase PowerPointScriptGenerator
├─ licenses/            # Licencias en múltiples idiomas
│  ├─ LICENSE_ES       # Español
│  ├─ LICENSE_EN       # English
│  ├─ LICENSE_DE       # Deutsch
│  ├─ LICENSE_FR       # Français
│  └─ LICENSE_PT       # Português
├─ venv/                # Entorno virtual Python
├─ node_modules/        # Dependencias Node.js
├─ .env                 # API key y credenciales (NO SUBIR A GIT)
├─ .env.example         # Plantilla de configuración
├─ .gitignore           # Archivos ignorados
├─ settings.yaml        # Configuración principal
├─ main.py              # Punto de entrada principal
├─ package.json         # Dependencias Node.js
├─ requirements.txt     # Dependencias Python
└─ README.md            # Este archivo
```

---

## 🛠️ Solución de Problemas

### ❌ Error: "API key no configurada"

> [!WARNING]
> Verifica que el archivo `.env` exista en la raíz del proyecto y contenga tu API key.

```bash
# Verificar que existe
ls -la .env

# Verificar el contenido (sin mostrar la key completa)
head -c 20 .env && echo "..."

# Si no existe, créalo
echo "sk-or-v1-tu-api-key-aqui" > .env
```

**Formato correcto del `.env`:**
```
sk-or-v1-1234567890abcdef...
```

**Formato INCORRECTO:**
```
API_KEY=sk-or-v1-...  ❌ (No uses variables)
"sk-or-v1-..."        ❌ (No uses comillas)
sk-or-v1-... \n       ❌ (No dejes espacios o saltos de línea)
```

> [!TIP]
> El archivo `.env` debe contener **solo la API key**, sin `API_KEY=`, sin comillas, sin espacios extras.

### ❌ Error: "Node.js no está instalado"

```bash
# Verifica la instalación
node --version
npm --version

# Si no está instalado:
# Ubuntu/Debian
sudo apt install nodejs npm

# macOS
brew install node
```

### ❌ Error: "Cannot find module 'docx'"

```bash
# Reinstala las dependencias
npm install
```

### ❌ Error: "No module named 'openpyxl'"

```bash
# Activa el entorno virtual
source venv/bin/activate

# Instala openpyxl
pip install openpyxl
```

### ❌ El modelo genera código con errores

> [!TIP]
> Algunos modelos gratuitos pueden generar código de menor calidad. Prueba con Llama 3.3 70B o Gemini 2.0 Flash para mejores resultados gratuitos.

---

## 🗺️ Roadmap

- [x] Soporte para Word (.docx)
- [x] Soporte para Excel (.xlsx)
- [x] Soporte para PowerPoint (.pptx)
- [x] Arquitectura SaaS Multitenancy
- [x] Webhook de Auto-Despliegue
- [x] Auto-corrección Inteligente de IA (5 intentos)
- [x] Conexión a SQL Server
- [x] Generación de consultas SQL con IA
- [x] Reportes automáticos desde base de datos
- [ ] Soporte para PDF
- [ ] API REST completa
- [ ] Interfaz web
- [ ] Plantillas predefinidas
- [ ] Soporte para imágenes en documentos
- [ ] Generación de gráficos avanzados
- [ ] Soporte para más bases de datos (MySQL, PostgreSQL)

---

## 💌 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📎 Recursos

* [Documentación de docx](https://docx.js.org/)
* [Documentación de openpyxl](https://openpyxl.readthedocs.io/)
* [Documentación de pptxgenjs](https://gitbrent.github.io/PptxGenJS/)
* [OpenRouter API](https://openrouter.ai/docs)
* [OpenRouter Models](https://openrouter.ai/models)

---

## 🏆 Créditos

**GR Code Digital Solutions** – Equipo de desarrollo y mantenimiento.

💻 Creado para hacer que la generación de documentos sea simple y poderosa.

---

## 💙 Apoya El Proyecto

<div align="center">

Si este proyecto te ha sido útil, considera apoyarlo a través de **GitHub Sponsors**.  
Tu contribución ayuda a mantener el desarrollo activo y mejorar futuras versiones.

</div>

---

<div align="center">

<img src="https://avatars.githubusercontent.com/u/186231665?v=4" width="90" style="border-radius: 50%; margin-bottom: 12px;"/>

<p style="font-size: 22px; font-weight: 800; margin: 0;">JoseEduardoGR</p>

<p>
<strong>Desarrollador • Python • C++ • Node</strong><br/>
🚀 Avanza aunque duela, cada salto te acerca a la versión que nadie creía posible.
</p>

<p>
<a href="https://github.com/JoseEduardoGR?tab=followers">⭐ Seguir en GitHub</a>
</p>

<a href="https://github.com/sponsors/JoseEduardoGR">
<img src="https://img.shields.io/badge/Sponsor_Me-FF4081?style=for-the-badge&logo=githubsponsors&logoColor=white" height="44"/>
</a>

</div>

---

## 📄 Licencia

Esta obra está protegida por una **Licencia Personalizada**  
*(Gratuita para uso personal, comercial requiere contacto)*

Puedes consultar las versiones disponibles en su **idioma respectivo**:

- 🇪🇸 [Español](licenses/LICENSE_ES)  
- 🇬🇧 [English](licenses/LICENSE_EN)  
- 🇩🇪 [Deutsch](licenses/LICENSE_DE)  
- 🇫🇷 [Français](licenses/LICENSE_FR)  
- 🇵🇹 [Português](licenses/LICENSE_PT)

> [!IMPORTANT]
> **Uso Personal:** Completamente gratuito  
> **Uso Comercial:** Requiere licencia. Contacta a [gonzalezrosalesjoseeduardo@gmail.com](mailto:gonzalezrosalesjoseeduardo@gmail.com)

---

<div align="center">

**Hecho con ❤️ por GR Code Digital Solutions**

<kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Awesome</kbd>

</div>
