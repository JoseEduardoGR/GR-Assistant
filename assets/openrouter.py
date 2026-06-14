import requests

class OpenRouterCatalog:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/models"
        self.all_models = self._fetch_models()

    def _fetch_models(self):
        """Descarga el catálogo completo de la API."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Error al conectar con OpenRouter: {e}")
            return []

    def filter_models(self, free_only=True, modality="text->text"):
        """Filtra y organiza la información de los modelos.

        modality puede ser "text->text" o "text+image->text" (visión).
        """
        filtered = []
        for m in self.all_models:
            is_free    = m.get('pricing', {}).get('prompt') == "0"
            arch       = m.get('architecture', {})
            m_modality = arch.get('modality') or arch.get('input_modalities', '')

            if free_only and not is_free:
                continue

            # Comparación flexible: acepta tanto el string exacto como listas
            if modality:
                if isinstance(m_modality, list):
                    # Algunos modelos devuelven lista de modalidades de entrada
                    has_image = "image" in m_modality
                    if modality == "text+image->text" and not has_image:
                        continue
                    if modality == "text->text" and has_image:
                        continue
                elif m_modality != modality:
                    continue
            
            # Construimos el link dinámicamente usando el ID
            model_id = m['id']
            link = f"https://openrouter.ai/models/{model_id}"
                
            filtered.append({
                "id": model_id,
                "name": m.get('name', 'Sin nombre'),
                "context": m.get('context_length', 0),
                "description": m.get('description', 'Sin descripción disponible.'),
                "link": link
            })
        return filtered

# --- PRUEBA DEL SCRIPT ---
'''
catalog = OpenRouterCatalog()
modelos_texto = catalog.filter_models(free_only=True, modality="text->text")

print(f"--- LISTADO DE MODELOS GRATUITOS ({len(modelos_texto)}) ---")
for m in modelos_texto[:5]:  # Mostramos los primeros 5 para no saturar
    print(f"\n🌟 NOMBRE: {m['name']}")
    print(f"🔗 LINK: {m['link']}")
    print(f"🧠 CONTEXTO: {m['context']} tokens")
    # Cortamos la descripción si es muy larga para que se vea bien en terminal
    desc = (m['description'][:100] + '...') if len(m['description']) > 100 else m['description']
    print(f"📝 DESC: {desc}")
    print("-" * 50)     
'''