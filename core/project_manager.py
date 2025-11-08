from pathlib import Path
from datetime import datetime

class ProjectManager:
    def __init__(self, project_root="project"):
        self.project_root = Path(project_root)
        self.setup_directories()
        
    def setup_directories(self):
        """Создает структуру папок проекта"""
        directories = ["images", "previews", "gcode", "outputs"]
        for directory in directories:
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)
    
    def get_unique_filename(self, base_name, extension, subfolder=""):
        """Генерирует уникальное имя файла с timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = base_name.replace(" ", "_").lower()
        filename = f"{safe_name}_{timestamp}.{extension}"
        
        if subfolder:
            return self.project_root / subfolder / filename
        return self.project_root / filename