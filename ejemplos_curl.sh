
#!/bin/bash

# Ejemplos de uso de la API de GR Docs con base de datos

# Configuración
API_URL="http://localhost:8000"
DATABASE="tu_base_datos"  # Cambia esto por el nombre de tu base de datos

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Ejemplos de API - GR Docs Database               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Listar tablas
echo "1. Listar tablas de la base de datos:"
echo "   curl \"${API_URL}/database/tables?database=${DATABASE}\""
echo ""

# 2. Generar consulta con IA
echo "2. Generar consulta SQL con IA:"
echo "   curl -X POST ${API_URL}/database/generate-query \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"request\":\"muéstrame los últimos 10 registros\",\"database\":\"${DATABASE}\"}'"
echo ""

# 3. Ejecutar consulta
echo "3. Ejecutar consulta SQL:"
echo "   curl -X POST ${API_URL}/database/query \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"query\":\"SELECT TOP 10 * FROM tabla\",\"database\":\"${DATABASE}\"}'"
echo ""

# 4. Generar reporte en Word
echo "4. Generar reporte en Word con información de tablas:"
echo "   curl -X POST ${API_URL}/database/report \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"request\":\"información general de todas las tablas de la base de datos\",\"report_type\":\"word\",\"database\":\"${DATABASE}\"}' \\"
echo "     --output reporte_tablas.docx"
echo ""

# 5. Generar reporte en Excel
echo "5. Generar reporte en Excel:"
echo "   curl -X POST ${API_URL}/database/report \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"request\":\"listado de todas las tablas con sus columnas\",\"report_type\":\"excel\",\"database\":\"${DATABASE}\"}' \\"
echo "     --output reporte_tablas.xlsx"
echo ""

# 6. Generar reporte en PowerPoint
echo "6. Generar reporte en PowerPoint:"
echo "   curl -X POST ${API_URL}/database/report \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"request\":\"presentación con estadísticas de la base de datos\",\"report_type\":\"powerpoint\",\"database\":\"${DATABASE}\"}' \\"
echo "     --output reporte_tablas.pptx"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    EJEMPLO COMPLETO                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Para generar un reporte Word con información de las tablas:"
echo ""
echo "curl -X POST http://localhost:8000/database/report \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{" 
echo "    \"request\": \"Genera un reporte completo con información general de todas las tablas: nombre de cada tabla, cantidad de columnas, tipos de datos y descripción general\"," 
echo "    \"report_type\": \"word\"," 
echo "    \"database\": \"${DATABASE}\"" 
echo "  }' \\"
echo "  --output reporte_base_datos.docx"
echo ""
