# Конфигурационные константы
class AppConfig:
    WINDOW_TITLE = "🖋️ Фото → G-code для CNC - Расширенная версия"
    WINDOW_SIZE = "1000x800"
    PROJECT_ROOT = "cnc_project"
    
    # Стили изображений
    STYLES = {
        "simple": ["sketch", "contour", "silhouette", "blurred"],
        "advanced": ["pencil", "pen_hatching", "makelangelo5", "portrait"]
    }
    
    # Настройки G-code - ВЫКЛЮЧАЕМ случайности для точного соответствия
    GCODE_CONFIG = {
        "scale_x": 0.5,
        "scale_y": 0.5,
        "offset_x": 50,
        "offset_y": 50,
        "feed_rate_drawing": 500,
        "feed_rate_travel": 2000,
        "pen_up_delay": 0.3,
        "pen_down_delay": 0.3,
        "randomize_contours": False,  # ВЫКЛЮЧЕНО - контуры в естественном порядке
        "add_noise": False           # ВЫКЛЮЧЕНО - без случайных смещений
    }
    
    # Настройки обработки изображений - улучшаем качество контуров
    IMAGE_CONFIG = {
        "image_size": (400, 400),
        "epsilon_factor": 0.005,     # Уменьшено для более точных контуров
        "min_contour_length": 5,     # Увеличено для фильтрации мелких шумов
        "GCODE_CONFIG": GCODE_CONFIG
    }
    
    # Цвета интерфейса
    COLORS = {
        "bg_primary": "#2c3e50",
        "bg_secondary": "#34495e",
        "text_primary": "#ecf0f1",
        "text_secondary": "#bdc3c7",
        "accent_blue": "#3498db",
        "accent_green": "#2ecc71",
        "accent_orange": "#f39c12",
        "accent_purple": "#9b59b6",
        "accent_red": "#e74c3c"
    }