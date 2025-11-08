import tkinter as tk
from tkinter import ttk
from utils.config import AppConfig

class PreviewPanel:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.canvas_frames = {}
        self.setup_ui()
    
    def setup_ui(self):
        # Выбор режима превью
        preview_mode_frame = tk.Frame(self.parent, bg=AppConfig.COLORS["bg_primary"])
        preview_mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.app.preview_mode = tk.StringVar(value="simple")
        tk.Radiobutton(preview_mode_frame, text="Простые стили", 
                      variable=self.app.preview_mode, value="simple",
                      command=self.app.update_previews, 
                      bg=AppConfig.COLORS["bg_primary"], fg="white",
                      font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(preview_mode_frame, text="Продвинутые стили", 
                      variable=self.app.preview_mode, value="advanced",
                      command=self.app.update_previews,
                      bg=AppConfig.COLORS["bg_primary"], fg="white",
                      font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=10)

        # Контейнер для превью
        self.app.preview_container = tk.Frame(self.parent, bg=AppConfig.COLORS["bg_primary"])
        self.app.preview_container.pack(fill=tk.BOTH, expand=True)
        
        self.setup_previews()
    
    def setup_previews(self):
        # Очищаем контейнер
        for widget in self.app.preview_container.winfo_children():
            widget.destroy()

        # Определяем стили для текущего режима
        styles = self.get_current_styles()
        
        # Создаем превью
        self.canvas_frames = {}
        for i, (label, style) in enumerate(styles):
            row = i // 2
            col = i % 2
            
            frame = ttk.LabelFrame(self.app.preview_container, text=label, width=200, height=200)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            frame.pack_propagate(False)
            
            canvas = tk.Canvas(frame, width=180, height=180, 
                             bg=AppConfig.COLORS["bg_secondary"], highlightthickness=0)
            canvas.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            self.canvas_frames[style] = canvas

        # Настройка grid
        self.app.preview_container.grid_rowconfigure(0, weight=1)
        self.app.preview_container.grid_rowconfigure(1, weight=1)
        self.app.preview_container.grid_columnconfigure(0, weight=1)
        self.app.preview_container.grid_columnconfigure(1, weight=1)
    
    def get_current_styles(self):
        if self.app.preview_mode.get() == "simple":
            return [
                ("Оригинал", "original"),
                ("Эскиз", "sketch"), 
                ("Контур", "contour"),
                ("Силуэт", "silhouette"),
                ("Размыто", "blurred")
            ]
        else:
            return [
                ("Оригинал", "original"),
                ("Карандаш", "pencil"),
                ("Штриховка", "pen_hatching"), 
                ("Makelangelo", "makelangelo5"),
                ("Портрет", "portrait")
            ]