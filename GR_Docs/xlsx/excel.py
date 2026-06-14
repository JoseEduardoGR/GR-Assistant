import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from GR_Docs.base_generator import BaseDocumentGenerator

class ExcelScriptGenerator(BaseDocumentGenerator):
    """Genera scripts Python para crear archivos Excel usando el modelo de IA."""
    
    def __init__(self, settings_path="settings.yaml", verbose=None):
        super().__init__(
            settings_path=settings_path,
            verbose=verbose,
            prompt_key="prompt_xlsx",
            default_prompt_path="GR_Docs/xlsx/prompt.gr",
            cache_folder="GR_Docs/xlsx/cache",
            output_ext=".xlsx",
            script_ext=".py",
            runtime="python"
        )
