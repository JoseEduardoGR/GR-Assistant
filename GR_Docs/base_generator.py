import os
import sys
import uuid
import yaml
import subprocess
from pathlib import Path

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from assets.engine import OpenRouterEngine

class BaseDocumentGenerator:
    """Clase base para la generación de documentos con sistema de auto-corrección."""
    
    def __init__(self, settings_path="settings.yaml", verbose=None, prompt_key=None, default_prompt_path=None, cache_folder=None, output_ext=None, script_ext=None, runtime="node"):
        self.settings = self._load_settings(settings_path)
        
        if verbose is None:
            verbose = self.settings.get("verbose", True)
        
        self.engine = OpenRouterEngine(settings_path, verbose=verbose)
        self.prompt_path = self.settings.get(prompt_key, default_prompt_path)
        
        # Rutas relativas o absolutas - Siempre ancladas al project_root
        self.cache_dir = Path(project_root) / cache_folder
            
        self.output_dir = self.cache_dir / "output"
        self._expected_output = None
        self.output_ext = output_ext
        self.script_ext = script_ext
        self.runtime = runtime
        self.verbose = verbose
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_settings(self, path: str) -> dict:
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            if self.verbose:
                print(f"[BaseGenerator] settings.yaml no encontrado en '{path}'")
            return {}

    def _load_prompt(self, user_preferences: dict = None, user_files_context: list = None) -> str:
        """Carga el prompt y añade preferencias y archivos visuales del usuario si existen."""
        try:
            with open(self.prompt_path) as f:
                base_prompt = f.read().strip()
                
            if user_preferences:
                if 'prompt_style' in user_preferences and user_preferences['prompt_style']:
                    base_prompt += f"\n\nInstrucciones Específicas del Usuario:\n{user_preferences['prompt_style']}"
                
                if 'company_info' in user_preferences and user_preferences['company_info']:
                    base_prompt += f"\n\nInformación de la Empresa del Usuario (para membretes, logos y referencias):\n{user_preferences['company_info']}"
                    
                if 'database_schema' in user_preferences and user_preferences['database_schema']:
                    base_prompt += f"\n\nContexto / Esquema de Base de Datos del Usuario (para reportes y Excels exactos):\n{user_preferences['database_schema']}"
            
            if user_files_context:
                base_prompt += "\n\nRECURSOS GRÁFICOS DISPONIBLES EN EL SERVIDOR:"
                base_prompt += "\nEl usuario ha subido los siguientes archivos gráficos. Las rutas absolutas a usar en tu código son:"
                for f in user_files_context:
                    base_prompt += f"\n - Ruta: '{f['path']}' (Etiqueta o propósito: '{f['name']}')"
                base_prompt += "\n\nINSTRUCCIÓN CRÍTICA PARA RECURSOS: A MENOS que el usuario pida no usarlos, DEBES obligatoriamente incrustar estas imágenes en el documento utilizando el código apropiado para su propósito (ej. si su etiqueta dice 'encabezado', incrusta la imagen de esa ruta en el encabezado del documento ajustada al 100% de ancho)."
                
            return base_prompt
        except FileNotFoundError:
            if self.verbose:
                print(f"[BaseGenerator] Prompt no encontrado en '{self.prompt_path}'")
            return ""

    def _clean_script(self, content: str) -> str:
        if not content:
            return ""
        lines = content.split('\n')
        cleaned_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block or not line.strip().startswith('```'):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def generate_script(self, user_request: str, previous_error: str = None, previous_code: str = None, user_preferences: dict = None, user_files_context: list = None) -> tuple[str, str]:
        base_prompt = self._load_prompt(user_preferences, user_files_context)
        
        output_id = str(uuid.uuid4())
        output_filename = f"{output_id}{self.output_ext}"
        output_path = self.output_dir / output_filename
        
        if previous_error and previous_code:
            full_prompt = f"""{base_prompt}
            
El código generado anteriormente falló. 
Código que falló:
```
{previous_code}
```

Error obtenido:
```
{previous_error}
```

Por favor, corrige el error y genera SOLO el código completo corregido.
IMPORTANTE: El archivo de salida DEBE guardarse en la ruta: {output_path}
"""
        else:
            if self.runtime == "python":
                log_instruction = "Al final del script, asegúrate de incluir un print() indicando que el archivo se generó exitosamente con su tamaño."
            else:
                log_instruction = "Al final del script, asegúrate de incluir un console.log indicando que el archivo se generó exitosamente."
                if self.script_ext == ".cjs":
                    log_instruction = "Genera SOLO el código JavaScript completo usando CommonJS (require), sin explicaciones adicionales.\n" + log_instruction
                    
            full_prompt = f"""{base_prompt}

Solicitud del usuario:
{user_request}

IMPORTANTE: El archivo de salida DEBE guardarse en la ruta: {output_path}

Genera SOLO el código completo, sin explicaciones adicionales.
{log_instruction}"""
            
        ai_model = user_preferences.get('ai_model') if user_preferences else None
        override_key = user_preferences.get('openrouter_key') if user_preferences else None
        script_content = self.engine.process(full_prompt, override_model=ai_model, override_api_key=override_key)
        script_content = self._clean_script(script_content)
        
        script_id = str(uuid.uuid4())
        script_filename = f"{script_id}{self.script_ext}"
        script_path = self.cache_dir / script_filename
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
            
        self._expected_output = str(output_path)
        return str(script_path), script_content

    def execute_script(self, script_path: str) -> tuple[bool, str, str]:
        """Ejecuta el script. Retorna (éxito, ruta_o_error, stderr)"""
        abs_script_path = os.path.abspath(script_path)
        cmd = ['node', abs_script_path] if self.runtime == "node" else [sys.executable, abs_script_path]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.getcwd()
            )
            
            if result.returncode != 0:
                return False, result.stderr, result.stderr
                
            if self._expected_output and os.path.exists(self._expected_output):
                return True, self._expected_output, ""
                
            files = list(self.output_dir.glob(f"*{self.output_ext}"))
            if not files:
                return False, f"No se encontró el archivo {self.output_ext} generado", ""
                
            latest = max(files, key=lambda p: p.stat().st_mtime)
            return True, str(latest), ""
            
        except subprocess.TimeoutExpired:
            return False, "Script execution timeout (60s)", "Timeout"
        except FileNotFoundError as e:
            return False, f"{self.runtime} no está instalado o no está en el PATH", str(e)

    def generate_and_execute(self, user_request: str, user_preferences: dict = None, user_files_context: list = None) -> tuple[str, str]:
        """Genera y ejecuta con auto-corrección de hasta 5 intentos."""
        self.engine.clear_history()
        max_attempts = 5
        previous_error = None
        previous_code = None
        
        for attempt in range(1, max_attempts + 1):
            if self.verbose:
                print(f"[BaseGenerator] Intento {attempt}/{max_attempts} para generar documento...")
                
            script_path, script_content = self.generate_script(
                user_request=user_request, 
                previous_error=previous_error, 
                previous_code=previous_code,
                user_preferences=user_preferences,
                user_files_context=user_files_context
            )
            
            if script_content.startswith("[Error"):
                return "", script_content
                
            success, result_path_or_error, stderr = self.execute_script(script_path)
            
            if success:
                return script_path, result_path_or_error
            else:
                if self.verbose:
                    print(f"[BaseGenerator] Error en intento {attempt}: {result_path_or_error}")
                previous_error = stderr
                previous_code = script_content
                
        # Si llega aquí, falló 5 veces. Pedir solución propuesta a la IA
        solution_prompt = f"""El siguiente código ha fallado persistentemente después de 5 intentos.
Código:
{previous_code}
Error:
{previous_error}
Requerimiento del usuario: {user_request}

Analiza brevemente por qué falla y propón una solución clara para que el usuario la intente (ej. faltan dependencias, el usuario debe pedir algo distinto, etc). No generes más código."""
        
        ai_model = user_preferences.get('ai_model') if user_preferences else None
        override_key = user_preferences.get('openrouter_key') if user_preferences else None
        ai_solution = self.engine.process(solution_prompt, override_model=ai_model, override_api_key=override_key)
        return "", f"Error tras 5 intentos. Detalle del último error:\n{previous_error}\n\nSolución propuesta por la IA:\n{ai_solution}"

    def download(self, doc_path: str, custom_name: str = None) -> str:
        doc_file = Path(doc_path)
        if not doc_file.exists():
            raise FileNotFoundError(f"Documento no encontrado: {doc_path}")
            
        if not custom_name:
            custom_name = self._generate_filename(doc_path)
            
        custom_name = self._sanitize_filename(custom_name)
        if not custom_name.endswith(self.output_ext):
            custom_name += self.output_ext
            
        new_path = self.output_dir / custom_name
        doc_file.rename(new_path)
        return str(new_path)

    def _generate_filename(self, doc_path: str) -> str:
        prompt = (
            "Basándote en el contexto, "
            "genera un nombre de archivo corto y descriptivo (máximo 50 caracteres, sin espacios, usa guiones). "
            "Responde SOLO con el nombre del archivo, sin extensión ni explicaciones."
        )
        filename = self.engine.process(prompt).strip()
        return filename.replace('"', '').replace("'", '').strip()

    def _sanitize_filename(self, filename: str) -> str:
        if filename.endswith(self.output_ext):
            filename = filename[:-len(self.output_ext)]
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '-')
        filename = filename.replace(' ', '-')
        return filename[:50]
