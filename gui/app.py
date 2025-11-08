import tkinter as tk
from tkinter import filedialog, messagebox
import os
import cv2
from datetime import datetime

from core.project_manager import ProjectManager
from core.image_processor import ImageProcessor
from gui.components.control_panel import ControlPanel
from gui.components.preview_panel import PreviewPanel
from gui.components.serial_controller import SerialController
from utils.config import AppConfig
from utils.helpers import cv2_to_tk

class AdvancedCNCApp:
    def __init__(self, root):
        self.root = root
        self.setup_app()
        self.setup_core_components()
        self.setup_gui_components()
        self.setup_ui()
    
    def setup_app(self):
        """Базовая настройка приложения"""
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(AppConfig.WINDOW_SIZE)
        self.root.config(bg=AppConfig.COLORS["bg_primary"])
        
        self.image_path = None
        self.original_image = None
        self.processed_images = {}
        self.final_png_path = None
        self.last_gcode_path = None
    
    def setup_core_components(self):
        self.pm = ProjectManager(AppConfig.PROJECT_ROOT)
        
        # Создаем полную конфигурацию, включая G-code настройки
        full_config = AppConfig.IMAGE_CONFIG.copy()
        full_config['GCODE_CONFIG'] = AppConfig.GCODE_CONFIG
        
        self.processor = ImageProcessor(self.pm, full_config)
        self.serial_controller = SerialController(self)
    
    def setup_gui_components(self):
        """Инициализация GUI компонентов"""
        # Эти компоненты будут созданы в setup_ui
        pass
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Заголовок
        self.setup_header()
        
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg=AppConfig.COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Левая панель - управление
        left_frame = tk.Frame(main_frame, bg=AppConfig.COLORS["bg_secondary"], 
                            relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Правая панель - превью
        right_frame = tk.Frame(main_frame, bg=AppConfig.COLORS["bg_primary"])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Инициализация компонентов
        self.control_panel = ControlPanel(left_frame, self)
        self.preview_panel = PreviewPanel(right_frame, self)
        
        # Статус бар и прогресс бар
        self.setup_status_bars()
        
        # Обновляем порты при запуске
        self.serial_controller.update_ports()
    
    def setup_header(self):
        """Настройка заголовка приложения"""
        title = tk.Label(
            self.root,
            text="🖋️ Фото → Рисунок → G-code - Полная версия",
            font=("Segoe UI", 18, "bold"),
            bg=AppConfig.COLORS["bg_primary"], 
            fg=AppConfig.COLORS["text_primary"]
        )
        title.pack(pady=15)

        subtitle = tk.Label(
            self.root,
            text="Загрузите фото → выберите стиль → сохраните PNG или создайте G-code → отправьте на принтер",
            font=("Segoe UI", 10),
            bg=AppConfig.COLORS["bg_primary"], 
            fg=AppConfig.COLORS["text_secondary"]
        )
        subtitle.pack(pady=5)
    
    def setup_status_bars(self):
        """Настройка статус бара и прогресс бара"""
        self.status = tk.Label(self.root, text="Готово. Загрузите фото.", 
                             bg=AppConfig.COLORS["bg_primary"], 
                             fg=AppConfig.COLORS["text_secondary"], 
                             font=("Segoe UI", 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.progress = tk.ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)
    
    # Основные методы приложения
    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not self.image_path:
            return

        self.original_image = cv2.imread(self.image_path)
        if self.original_image is None:
            self.show_error("Ошибка", "Не удалось загрузить изображение.")
            return

        self.display_image(self.original_image, "original")
        self.file_label.config(text=os.path.basename(self.image_path))
        self.update_status("Фото загружено. Выберите стиль и нажмите 'Обработать'.")
        self.convert_btn['state'] = 'normal'
        self.log(f"Загружено изображение: {os.path.basename(self.image_path)}")
    
    def process_image(self):
        if self.original_image is None:
            self.show_warning("Внимание", "Сначала загрузите фото!")
            return

        self.progress.start()
        self.log("Начинаем обработку изображения...")

        try:
            # Определяем какие стили обрабатывать
            if self.preview_mode.get() == "simple":
                styles_to_process = AppConfig.STYLES["simple"]
                current_style = self.simple_style_var.get()
            else:
                styles_to_process = AppConfig.STYLES["advanced"]
                current_style = self.advanced_style_var.get()

            # Обрабатываем все стили текущего режима
            for style in styles_to_process:
                self.processed_images[style] = self.processor.style_converter.apply_style(
                    self.original_image, style
                )
                self.log(f"Обработан стиль: {style}")

            # Обновляем превью
            self.display_current_images()

            self.update_status("Изображения обработаны. Можно сохранять или создавать G-code.")
            self.save_btn['state'] = 'normal'
            self.gcode_btn['state'] = 'normal'

            self.log("✓ Обработка завершена успешно!")

        except Exception as e:
            self.log(f"✗ Ошибка обработки: {e}")
            self.show_error("Ошибка", f"Не удалось обработать изображение:\n{e}")
        
        finally:
            self.progress.stop()
    
    def display_image(self, img, canvas_name):
        """Отображает изображение на указанном canvas"""
        if img is None or canvas_name not in self.preview_panel.canvas_frames:
            return

        canvas = self.preview_panel.canvas_frames[canvas_name]
        canvas_w = canvas.winfo_width() - 10
        canvas_h = canvas.winfo_height() - 10
        
        if canvas_w <= 1 or canvas_h <= 1:
            canvas_w, canvas_h = 180, 180

        # Получаем размеры изображения
        if len(img.shape) == 3:
            h, w = img.shape[:2]
        else:
            h, w = img.shape

        scale = min(canvas_w / w, canvas_h / h)
        new_w, new_h = int(w * scale), int(h * scale)

        # Конвертируем и отображаем
        resized_img = cv2.resize(img, (new_w, new_h))
        tk_img = cv2_to_tk(resized_img)

        canvas.delete("all")
        x = (canvas_w - new_w) // 2 + 5
        y = (canvas_h - new_h) // 2 + 5
        canvas.create_image(x, y, anchor=tk.NW, image=tk_img)
        canvas.image = tk_img
    
    def display_current_images(self):
        """Отображает все текущие изображения"""
        self.display_image(self.original_image, "original")
        for style, img in self.processed_images.items():
            if style in self.preview_panel.canvas_frames:
                self.display_image(img, style)
    
    def update_previews(self):
        """Обновляет панель превью"""
        self.preview_panel.setup_previews()
        if self.original_image is not None:
            self.display_current_images()
    
    def log(self, message):
        """Добавляет запись в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def update_status(self, msg):
        """Обновляет статус бар"""
        self.status.config(text=msg)
    
    def show_error(self, title, message):
        """Показывает сообщение об ошибке"""
        messagebox.showerror(title, message)
    
    def show_warning(self, title, message):
        """Показывает предупреждение"""
        messagebox.showwarning(title, message)
    
    def show_info(self, title, message):
        """Показывает информационное сообщение"""
        messagebox.showinfo(title, message)

    def save_png(self):
        """Сохраняет обработанное изображение как PNG"""
        if not self.processed_images:
            self.show_warning("Внимание", "Нет обработанных изображений для сохранения.")
            return

        # Определяем текущий выбранный стиль
        if self.preview_mode.get() == "simple":
            current_style = self.simple_style_var.get()
        else:
            current_style = self.advanced_style_var.get()

        if current_style not in self.processed_images:
            self.show_warning("Внимание", "Выбранный стиль не обработан.")
            return

        output_dir = filedialog.askdirectory(title="Папка для сохранения PNG")
        if not output_dir:
            return

        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        
        # Получаем читаемое название стиля
        style_names = {
            "sketch": "Эскиз", "contour": "Контур", "silhouette": "Силуэт", "blurred": "Размыто",
            "pencil": "Карандаш", "pen_hatching": "Штриховка", 
            "makelangelo5": "Makelangelo", "portrait": "Портрет"
        }
        style_name = style_names.get(current_style, current_style)
        
        img = self.processed_images[current_style]
        filename = f"{base_name}_{style_name}.png"
        path = os.path.join(output_dir, filename)
        cv2.imwrite(path, img)

        self.final_png_path = path
        self.update_status(f"Сохранено: {filename}")
        self.log(f"Сохранен PNG: {filename}")
        self.show_info("Готово!", f"Файл сохранён:\n{path}")

    def create_gcode(self):
        """Создает G-code из обработанного изображения"""
        if not self.processed_images:
            self.show_warning("Внимание", "Нет обработанных изображений для создания G-code.")
            return

        # Определяем текущий выбранный стиль
        if self.preview_mode.get() == "simple":
            current_style = self.simple_style_var.get()
        else:
            current_style = self.advanced_style_var.get()

        if current_style not in self.processed_images:
            self.show_warning("Внимание", "Выбранный стиль не обработан.")
            return

        self.progress.start()
        self.log("Создаем G-code...")

        try:
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]
            
            # Используем конвертер для создания G-code
            processed_image = self.processed_images[current_style]
            contours = self.processor.find_contours(processed_image)
            gcode_commands = self.processor.gcode_generator.contours_to_gcode(contours)
            
            # Сохраняем G-code
            style_names = {
                "sketch": "sketch", "contour": "contour", "silhouette": "silhouette", 
                "blurred": "blurred", "pencil": "pencil", "pen_hatching": "pen_hatching",
                "makelangelo5": "makelangelo5", "portrait": "portrait"
            }
            style_suffix = style_names.get(current_style, current_style)
            
            gcode_path = self.pm.get_unique_filename(f"{base_name}_{style_suffix}", "gcode", "gcode")
            
            with open(gcode_path, 'w', encoding='utf-8') as f:
                for command in gcode_commands:
                    f.write(command + '\n')

            self.last_gcode_path = str(gcode_path)
            self.send_btn['state'] = 'normal'
            
            self.update_status(f"G-code создан: {len(gcode_commands)} команд, {len(contours)} контуров")
            self.log(f"✓ G-code создан: {os.path.basename(gcode_path)}")
            self.log(f"  Контуров: {len(contours)}, Команд: {len(gcode_commands)}")
            
            self.show_info("Готово!", 
                          f"G-code файл создан успешно!\n\n"
                          f"Файл: {os.path.basename(gcode_path)}\n"
                          f"Контуров: {len(contours)}\n"
                          f"Команд G-code: {len(gcode_commands)}")

        except Exception as e:
            self.log(f"✗ Ошибка создания G-code: {e}")
            self.show_error("Ошибка", f"Не удалось создать G-code:\n{e}")
        
        finally:
            self.progress.stop()

    def send_gcode_to_printer(self):
        """Отправляет G-code на принтер"""
        if not self.last_gcode_path:
            self.show_error("Ошибка", "Сначала создайте G-code")
            return
        
        self.progress.start()
        success = self.serial_controller.send_gcode_to_printer(self.last_gcode_path)
        self.progress.stop()
        
        if success:
            self.show_info("Успех", "G-code успешно отправлен на принтер!")
        else:
            self.show_error("Ошибка", "Не удалось отправить G-code на принтер")