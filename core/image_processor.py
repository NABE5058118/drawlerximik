import cv2
import numpy as np
from pathlib import Path
from .style_converter import StyleConverter
from .gcode_generator import GCodeGenerator

class ImageProcessor:
    def __init__(self, project_manager, config):
        self.pm = project_manager
        self.config = config
        self.style_converter = StyleConverter()
        
        # Извлекаем настройки G-code из конфига или используем значения по умолчанию
        gcode_config = config.get('GCODE_CONFIG', {})
        self.gcode_generator = GCodeGenerator(gcode_config)
    
    def find_contours(self, image):
        """Находит и упрощает контуры на изображении"""
        # Используем RETR_EXTERNAL для получения только внешних контуров
        # или RETR_LIST для всех контуров
        contours, _ = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        min_length = self.config.get('min_contour_length', 5)  # Увеличим минимальную длину
        filtered_contours = [cnt for cnt in contours if cv2.arcLength(cnt, False) > min_length]
        
        simplified_contours = []
        epsilon_factor = self.config.get('epsilon_factor', 0.005)  # Уменьшим фактор упрощения
        
        for contour in filtered_contours:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) >= 2:  # Минимум 2 точки для линии
                simplified_contours.append(approx)
        
        return simplified_contours
    
    def create_preview(self, original_image, processed_image, contours, output_path):
        """Создает превью с контурами"""
        if len(original_image.shape) == 2:
            preview = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
        else:
            preview = original_image.copy()
        
        # Рисуем контуры разными цветами для наглядности
        colors = [
            (0, 0, 255),    # Красный
            (0, 255, 0),    # Зеленый  
            (255, 0, 0),    # Синий
            (0, 255, 255),  # Желтый
            (255, 0, 255),  # Пурпурный
            (255, 255, 0)   # Голубой
        ]
        
        for i, contour in enumerate(contours):
            color = colors[i % len(colors)]
            cv2.drawContours(preview, [contour], -1, color, 2)
            
            # Помечаем начало контура
            if len(contour) > 0:
                start_point = tuple(contour[0][0])
                cv2.circle(preview, start_point, 3, color, -1)
        
        cv2.imwrite(str(output_path), preview)
        return output_path
    
    def process_image(self, image_path, output_name=None, style=None):
        """Обрабатывает изображение и генерирует G-code"""
        if output_name is None:
            output_name = Path(image_path).stem
        
        original = cv2.imread(image_path)
        if original is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")
        
        # Ресайз изображения
        image_size = self.config.get('image_size', (400, 400))
        original = cv2.resize(original, image_size)
        
        if style is None:
            style = "sketch"
        
        # Применение стиля
        processed_image = self.style_converter.apply_style(original, style)
        
        # Улучшаем контраст для лучшего выделения контуров
        if len(processed_image.shape) == 2:  # Если изображение в градациях серого
            processed_image = cv2.equalizeHist(processed_image)
        
        # Находим контуры
        contours = self.find_contours(processed_image)
        
        # Создание превью
        preview_path = self.pm.get_unique_filename(f"{output_name}_{style}", "png", "previews")
        self.create_preview(original, processed_image, contours, preview_path)
        
        # Генерация G-code
        gcode_commands = self.gcode_generator.contours_to_gcode(contours)
        gcode_path = self.pm.get_unique_filename(f"{output_name}_{style}", "gcode", "gcode")
        
        with open(gcode_path, 'w', encoding='utf-8') as f:
            for command in gcode_commands:
                f.write(command + '\n')
        
        return {
            'preview': preview_path,
            'gcode': gcode_path,
            'contours_count': len(contours),
            'commands_count': len(gcode_commands),
            'processed_image': processed_image
        }