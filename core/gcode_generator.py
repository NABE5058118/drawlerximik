import random
import cv2
from utils.helpers import validate_gcode_line

class GCodeGenerator:
    def __init__(self, config=None):
        # Устанавливаем значения по умолчанию
        self.config = {
            "scale_x": 0.5,
            "scale_y": 0.5,
            "offset_x": 50,
            "offset_y": 50,
            "feed_rate_drawing": 500,
            "feed_rate_travel": 2000,
            "pen_up_delay": 0.3,
            "pen_down_delay": 0.3,
            "randomize_contours": False,  # Новый параметр для контроля случайности
            "add_noise": False           # Новый параметр для контроля шума
        }
        # Обновляем конфиг переданными значениями
        if config:
            self.config.update(config)
    
    def generate_header(self):
        return [
            "G21",        # Миллиметры
            "G90",        # Абсолютные координаты
            "G17",        # XY плоскость
            "G94",        # Единицы в минуту
            "G54",        # Система координат
            "M5",         # Выключить шпиндель (поднять перо)
            "G0 X0 Y0",   # Начальная позиция
            "G4 P1",      # Пауза 1 секунда
        ]
    
    def generate_footer(self):
        return [
            "M5",         # Поднять перо
            "G0 X0 Y0",   # Вернуться в начало
            "M30",        # Конец программы
        ]
    
    def validate_gcode(self, gcode_lines):
        """Валидирует G-code команды"""
        valid_lines = []
        for line_text in gcode_lines:
            if validate_gcode_line(line_text):
                valid_lines.append(line_text)
            else:
                print(f"Invalid G-code line skipped: {line_text}")
        return valid_lines
    
    def _sort_contours_by_area(self, contours):
        """Сортирует контуры по площади (от большего к меньшему)"""
        return sorted(contours, key=cv2.contourArea, reverse=True)
    
    def _sort_contours_spatially(self, contours):
        """Сортирует контуры пространственно (слева направо, сверху вниз)"""
        if not contours:
            return contours
            
        # Находим центры масс контуров
        moments = [cv2.moments(cnt) for cnt in contours]
        centers = []
        for i, M in enumerate(moments):
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centers.append((cx, cy, i))
            else:
                centers.append((0, 0, i))
        
        # Сортируем по Y, затем по X
        centers.sort(key=lambda x: (x[1] // 50, x[0] // 50))  # Группируем по областям 50x50 пикселей
        return [contours[i] for _, _, i in centers]
    
    def contours_to_gcode(self, contours):
        """Конвертирует контуры в G-code команды"""
        gcode_commands = []
        
        # Заголовок
        gcode_commands.extend(self.generate_header())
        gcode_commands.append(f"G1 F{self.config['feed_rate_travel']}")
        
        # Сортировка контуров для оптимального пути
        if self.config.get("randomize_contours", False):
            random.shuffle(contours)
        else:
            # Сортируем контуры пространственно для минимизации перемещений
            contours = self._sort_contours_spatially(contours)
        
        for contour in contours:
            if len(contour) < 2:
                continue
            
            # Начало контура
            start_point = contour[0][0]
            start_x = start_point[0] * self.config["scale_x"] + self.config["offset_x"]
            start_y = start_point[1] * self.config["scale_y"] + self.config["offset_y"]
            
            # Перемещение к началу контура
            gcode_commands.append(f"G0 X{start_x:.2f} Y{start_y:.2f}")
            
            # Опустить перо
            gcode_commands.append("M3 S0")
            
            if self.config["pen_down_delay"] > 0:
                gcode_commands.append(f"G4 P{self.config['pen_down_delay']}")
            
            # Установить скорость рисования
            gcode_commands.append(f"G1 F{self.config['feed_rate_drawing']}")
            
            # Рисование контура
            for i, point in enumerate(contour):
                x = point[0][0] * self.config["scale_x"] + self.config["offset_x"]
                y = point[0][1] * self.config["scale_y"] + self.config["offset_y"]
                
                # Добавляем небольшой шум только если включено и только для длинных контуров
                if self.config.get("add_noise", False) and len(contour) > 10:
                    x += random.uniform(-0.1, 0.1)  # Уменьшенный диапазон шума
                    y += random.uniform(-0.1, 0.1)
                
                gcode_commands.append(f"G1 X{x:.2f} Y{y:.2f}")
            
            # Замкнуть контур, если он не замкнут
            if not cv2.contourArea(contour) == 0:  # Если контур не замкнут
                end_x = contour[0][0][0] * self.config["scale_x"] + self.config["offset_x"]
                end_y = contour[0][0][1] * self.config["scale_y"] + self.config["offset_y"]
                gcode_commands.append(f"G1 X{end_x:.2f} Y{end_y:.2f}")
            
            # Поднять перо
            gcode_commands.append(f"G1 F{self.config['feed_rate_travel']}")
            gcode_commands.append("M5")
            
            if self.config["pen_up_delay"] > 0:
                gcode_commands.append(f"G4 P{self.config['pen_up_delay']}")
        
        # Завершение
        gcode_commands.extend(self.generate_footer())
        
        # Валидация всего G-code
        validated_commands = self.validate_gcode(gcode_commands)
        
        return validated_commands