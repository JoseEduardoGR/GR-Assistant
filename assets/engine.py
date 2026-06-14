import os
import sys
import base64
import mimetypes
import yaml
import requests
from colorama import init, Style, Fore
from dotenv import load_dotenv

# Agregar el directorio assets al path para importar openrouter
sys.path.insert(0, os.path.dirname(__file__))
from openrouter import OpenRouterCatalog

init(autoreset=True)

# Cargar variables de entorno
load_dotenv()

SETTINGS_PATH = "settings.yaml"


def _load_api_key() -> str:
    """Lee la API key del archivo .env."""
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not api_key:
        print(Fore.RED + "[Engine] OPENROUTER_API_KEY no encontrada en .env")
    return api_key


class Engine:
    def __init__(self, settings_path: str = SETTINGS_PATH, verbose: bool = True):
        self.settings = self._load_settings(settings_path)
        self.port     = self.settings.get("port") or 8000
        self.context  = self._load_context()
        self.history  = []
        self.verbose  = verbose

        # Obtener modelo desde settings.yaml o usar fallback
        configured_model = self.settings.get("model")
        
        if configured_model:
            # Si hay modelo configurado en el YAML, usarlo
            self.model = configured_model
            self.model_vision = configured_model  # Usar el mismo para visión por defecto
            if self.verbose:
                print(Fore.CYAN + f"[Engine] Modelo configurado: {self.model}")
        else:
            # Si no hay modelo en YAML, usar qwen/qwen3-coder:free como fallback
            self.model = "qwen/qwen3-coder:free"
            self.model_vision = "qwen/qwen3-coder:free"
            if self.verbose:
                print(Fore.YELLOW + f"[Engine] No hay modelo en settings.yaml, usando fallback: {self.model}")
        
        # Intentar obtener un modelo de visión específico si está disponible
        catalog = OpenRouterCatalog()
        models_vision = catalog.filter_models(free_only=True, modality="text+image->text")
        if models_vision:
            self.model_vision = models_vision[0]["id"]
            if self.verbose:
                print(Fore.CYAN + f"[Engine] Modelo visión: {self.model_vision}")
        else:
            if self.verbose:
                print(Fore.CYAN + f"[Engine] Modelo visión: {self.model_vision} (mismo que texto)")

    # ─── Config ───────────────────────────────────────────────────────────────

    def _load_settings(self, path: str) -> dict:
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(Fore.YELLOW + f"[Engine] settings.yaml no encontrado en '{path}', usando defaults.")
            return {}

    def _load_context(self) -> str:
        """Carga el contexto desde el archivo indicado en settings."""
        path = self.settings.get("context_file") or "context.gr"
        try:
            with open(path) as f:
                return f.read().strip()
        except FileNotFoundError:
            print(Fore.YELLOW + f"[Engine] Archivo de contexto no encontrado en '{path}'.")
            return ""

    # ─── Prompt ───────────────────────────────────────────────────────────────

    def process(self, prompt: str, image_path: str = None) -> str:
        """Construye el prompt completo y lo envía al modelo.

        Args:
            prompt:     Texto del usuario.
            image_path: Ruta opcional a una imagen (jpg, png, gif, webp).
        """
        if not prompt.strip():
            return ""

        if image_path:
            content = self._build_vision_content(prompt, image_path)
        else:
            content = prompt

        self.history.append({"role": "user", "content": content})
        response = self._run(use_vision=image_path is not None)
        self.history.append({"role": "assistant", "content": response})
        return response

    # ─── Helpers de imagen ────────────────────────────────────────────────────

    @staticmethod
    def _encode_image(image_path: str) -> tuple[str, str]:
        """Devuelve (mime_type, base64_data) de la imagen."""
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
            mime_type = "image/jpeg"  # fallback seguro
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return mime_type, b64

    def _build_vision_content(self, prompt: str, image_path: str) -> list:
        """Construye el content multimodal para mensajes con imagen."""
        mime_type, b64 = self._encode_image(image_path)
        return [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
            },
        ]

    def _build_messages(self, use_vision: bool = False) -> list:
        """Construye la lista de mensajes en formato OpenAI/OpenRouter."""
        messages = []

        if self.context:
            messages.append({"role": "system", "content": self.context})

        messages.extend(self.history)
        return messages

    def _run(self, use_vision: bool = False) -> str:
        """Envía el prompt al modelo y retorna la respuesta. Subclases pueden sobreescribir."""
        raise NotImplementedError(
            "Subclases deben implementar _run(). "
            "Usa OpenRouterEngine para modelos remotos."
        )

    # ─── History ──────────────────────────────────────────────────────────────

    def clear_history(self):
        """Resetea el historial de conversación."""
        self.history = []

    def get_history(self) -> list:
        """Retorna una copia del historial."""
        return list(self.history)

    # ─── Debug ────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Engine(model={self.model!r}, "
            f"port={self.port}, "
            f"history_len={len(self.history)})"
        )


# ─── OpenRouter Engine ────────────────────────────────────────────────────────

class OpenRouterEngine(Engine):
    """Engine que usa la API de OpenRouter para inferencia remota."""

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, settings_path: str = SETTINGS_PATH, verbose: bool = True):
        self.api_key = _load_api_key()
        super().__init__(settings_path, verbose)

    def _run(self, use_vision: bool = False) -> str:
        """Llama a la API de OpenRouter y retorna el texto de respuesta.

        Si use_vision=True, usa el modelo multimodal y envía la imagen en base64.
        """
        if not self.api_key:
            return "[Error] API key no configurada."

        model = self.model_vision if use_vision else self.model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }

        payload = {
            "model":    model,
            "messages": self._build_messages(use_vision=use_vision),
        }

        max_retries = 3
        retry_delay = 5  # segundos

        for attempt in range(max_retries):
            try:
                response = requests.post(self.API_URL, headers=headers, json=payload, timeout=60)
                
                # Si es rate limit (429), esperar y reintentar
                if response.status_code == 429:
                    error_data = response.json()
                    retry_after = error_data.get("error", {}).get("metadata", {}).get("retry_after_seconds", retry_delay)
                    
                    if attempt < max_retries - 1:
                        print(Fore.YELLOW + f"[Engine] Rate limit alcanzado. Reintentando en {retry_after}s... (intento {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(retry_after)
                        continue
                    else:
                        return f"[Error HTTP 429] Modelo temporalmente limitado. Intenta con otro modelo o espera {retry_after}s."
                
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
                
            except requests.exceptions.HTTPError as e:
                if attempt < max_retries - 1 and response.status_code == 429:
                    continue
                return f"[Error HTTP {response.status_code}] {response.text}"
            except Exception as e:
                if attempt < max_retries - 1:
                    print(Fore.YELLOW + f"[Engine] Error: {e}. Reintentando...")
                    import time
                    time.sleep(retry_delay)
                    continue
                return f"[Error] {e}"
        
        return "[Error] Máximo de reintentos alcanzado."
