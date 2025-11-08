import cv2
from PIL import Image, ImageTk
import tkinter as tk

def cv2_to_tk(image):
    """Конвертирует OpenCV изображение в формат для Tkinter"""
    if len(image.shape) == 3:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    pil_img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(pil_img)

def create_button(parent, text, command, color, **kwargs):
    """Создает стилизованную кнопку"""
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        relief="flat", borderwidth=0, font=("Segoe UI", 9),
        cursor="hand2", padx=10, pady=8, overrelief="solid", **kwargs
    )

def validate_gcode_line(line_text):
    """Валидирует строку G-code (если доступен pygcode)"""
    try:
        from pygcode import Line
        Line(line_text)
        return True
    except (ImportError, Exception):
        # Если pygcode недоступен или произошла ошибка, пропускаем валидацию
        return True