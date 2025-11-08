import tkinter as tk
from tkinter import ttk
from utils.helpers import create_button
from utils.config import AppConfig

class ControlPanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        # Загрузка изображения
        self.setup_load_section()
        
        # Выбор стилей
        self.setup_styles_section()
        
        # Обработка
        self.setup_process_section()
        
        # Подключение к принтеру
        self.setup_printer_section()
        
        # Лог
        self.setup_log_section()
    
    def setup_load_section(self):
        load_frame = tk.LabelFrame(self.parent, text="📁 Загрузка изображения", 
                                 bg=AppConfig.COLORS["bg_secondary"], fg="white", 
                                 font=("Segoe UI", 10, "bold"))
        load_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.app.load_btn = create_button(load_frame, "📁 Выбрать фото", 
                                        self.app.load_image, AppConfig.COLORS["accent_blue"])
        self.app.load_btn.pack(fill=tk.X, padx=5, pady=5)
        
        self.app.file_label = tk.Label(load_frame, text="Файл не выбран", 
                                     bg=AppConfig.COLORS["bg_secondary"], 
                                     fg=AppConfig.COLORS["text_secondary"],
                                     font=("Segoe UI", 8), wraplength=200)
        self.app.file_label.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_styles_section(self):
        """Настройка секции выбора стилей"""
        styles_frame = tk.LabelFrame(self.parent, text="🎨 Стили обработки", 
                                   bg=AppConfig.COLORS["bg_secondary"], fg="white", 
                                   font=("Segoe UI", 10, "bold"))
        styles_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Простые стили
        simple_frame = tk.Frame(styles_frame, bg=AppConfig.COLORS["bg_secondary"])
        simple_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(simple_frame, text="Простые стили:", bg=AppConfig.COLORS["bg_secondary"], 
                fg=AppConfig.COLORS["text_primary"], font=("Segoe UI", 9)).pack(anchor="w")
        
        self.app.simple_style_var = tk.StringVar(value="sketch")
        simple_styles = [
            ("Эскиз", "sketch"),
            ("Контур", "contour"), 
            ("Силуэт", "silhouette"),
            ("Размыто", "blurred")
        ]
        
        for text, value in simple_styles:
            tk.Radiobutton(simple_frame, text=text, variable=self.app.simple_style_var,
                          value=value, bg=AppConfig.COLORS["bg_secondary"], 
                          fg="white", selectcolor=AppConfig.COLORS["bg_primary"],
                          font=("Segoe UI", 8)).pack(anchor="w")

        # Продвинутые стили
        advanced_frame = tk.Frame(styles_frame, bg=AppConfig.COLORS["bg_secondary"])
        advanced_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(advanced_frame, text="Продвинутые стили:", 
                bg=AppConfig.COLORS["bg_secondary"], fg=AppConfig.COLORS["text_primary"],
                font=("Segoe UI", 9)).pack(anchor="w")
        
        self.app.advanced_style_var = tk.StringVar(value="pencil")
        advanced_styles = [
            ("✏️ Карандаш", "pencil"),
            ("🖊 Штриховка", "pen_hatching"),
            ("🔍 Makelangelo", "makelangelo5"),
            ("🎨 Портрет", "portrait")
        ]
        
        for text, value in advanced_styles:
            tk.Radiobutton(advanced_frame, text=text, variable=self.app.advanced_style_var,
                          value=value, bg=AppConfig.COLORS["bg_secondary"], 
                          fg="white", selectcolor=AppConfig.COLORS["bg_primary"],
                          font=("Segoe UI", 8)).pack(anchor="w")
    
    def setup_process_section(self):
        """Настройка секции обработки"""
        process_frame = tk.LabelFrame(self.parent, text="⚙️ Обработка", 
                                    bg=AppConfig.COLORS["bg_secondary"], fg="white", 
                                    font=("Segoe UI", 10, "bold"))
        process_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.app.convert_btn = create_button(process_frame, "🎨 Обработать фото", 
                                           self.app.process_image, AppConfig.COLORS["accent_green"])
        self.app.convert_btn.pack(fill=tk.X, padx=5, pady=5)
        self.app.convert_btn['state'] = 'disabled'
        
        self.app.save_btn = create_button(process_frame, "💾 Сохранить PNG", 
                                        self.app.save_png, AppConfig.COLORS["accent_orange"])
        self.app.save_btn.pack(fill=tk.X, padx=5, pady=5)
        self.app.save_btn['state'] = 'disabled'
        
        self.app.gcode_btn = create_button(process_frame, "⚙️ Создать G-code", 
                                         self.app.create_gcode, AppConfig.COLORS["accent_purple"])
        self.app.gcode_btn.pack(fill=tk.X, padx=5, pady=5)
        self.app.gcode_btn['state'] = 'disabled'
    
    def setup_printer_section(self):
        """Настройка секции подключения к принтеру"""
        printer_frame = tk.LabelFrame(self.parent, text="🖨️ Подключение к принтеру", 
                                    bg=AppConfig.COLORS["bg_secondary"], fg="white", 
                                    font=("Segoe UI", 10, "bold"))
        printer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Выбор порта
        port_frame = tk.Frame(printer_frame, bg=AppConfig.COLORS["bg_secondary"])
        port_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(port_frame, text="Порт:", bg=AppConfig.COLORS["bg_secondary"], 
                fg="white", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        
        self.app.port_var = tk.StringVar()
        self.app.port_combo = ttk.Combobox(port_frame, textvariable=self.app.port_var, 
                                          state="readonly", width=12, font=("Segoe UI", 8))
        self.app.port_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(port_frame, text="🔄", command=self.app.serial_controller.update_ports, 
                 bg=AppConfig.COLORS["accent_blue"], fg="white",
                 font=("Segoe UI", 8), width=3).pack(side=tk.LEFT, padx=2)
        
        # Кнопки подключения и отправки
        connect_btn = create_button(printer_frame, "🔗 Подключиться", 
                                  self.app.serial_controller.connect_printer, 
                                  AppConfig.COLORS["accent_red"])
        connect_btn.pack(fill=tk.X, padx=5, pady=2)
        
        self.app.send_btn = create_button(printer_frame, "📤 Отправить G-code", 
                                        self.app.send_gcode_to_printer, 
                                        AppConfig.COLORS["accent_orange"])
        self.app.send_btn.pack(fill=tk.X, padx=5, pady=2)
        self.app.send_btn['state'] = 'disabled'
        
        # Статус подключения
        self.app.connection_status = tk.Label(printer_frame, text="❌ Не подключено", 
                                            bg=AppConfig.COLORS["bg_secondary"], 
                                            fg=AppConfig.COLORS["accent_red"], 
                                            font=("Segoe UI", 9))
        self.app.connection_status.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_log_section(self):
        """Настройка секции лога"""
        log_frame = tk.LabelFrame(self.parent, text="📝 Лог выполнения", 
                                bg=AppConfig.COLORS["bg_secondary"], fg="white", 
                                font=("Segoe UI", 10, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.app.log_text = tk.Text(log_frame, height=8, width=30, 
                                  bg=AppConfig.COLORS["bg_primary"], 
                                  fg=AppConfig.COLORS["text_primary"],
                                  font=("Consolas", 8), relief=tk.FLAT)
        scrollbar = tk.Scrollbar(log_frame, command=self.app.log_text.yview)
        self.app.log_text.config(yscrollcommand=scrollbar.set)
        
        self.app.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)