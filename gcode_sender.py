import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import serial
import time

class GCodeSender:
    def __init__(self, root):
        self.root = root
        self.root.title("Отправка G-code")
        self.root.geometry("800x600")

        self.serial_conn = None
        self.gcode_lines = []
        self.current_line = 0

        self.setup_ui()

    def setup_ui(self):
        # Порт
        port_frame = tk.Frame(self.root)
        port_frame.pack(pady=10)

        tk.Label(port_frame, text="COM-порт:").grid(row=0, column=0)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1)
        tk.Button(port_frame, text="Обновить", command=self.update_ports).grid(row=0, column=2)
        tk.Button(port_frame, text="Подключиться", command=self.connect).grid(row=0, column=3)

        # Загрузка G-code
        tk.Button(self.root, text="Загрузить G-code", command=self.load_gcode).pack(pady=10)

        # Прогресс
        self.progress = ttk.Progressbar(self.root, mode='determinate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)

        # Статус
        self.status = tk.Label(self.root, text="Готов")
        self.status.pack(pady=5)

        # Кнопка отправки
        self.send_btn = tk.Button(self.root, text="Отправить G-code", command=self.send_gcode, state=tk.DISABLED)
        self.send_btn.pack(pady=10)

    def update_ports(self):
        import serial.tools.list_ports
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_var.set(ports[0])

    def connect(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Ошибка", "Выберите COM-порт")
            return
        try:
            self.serial_conn = serial.Serial(port, 115200, timeout=10)
            messagebox.showinfo("Успех", f"Подключено к {port}")
            self.send_btn['state'] = tk.NORMAL
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")

    def load_gcode(self):
        file_path = filedialog.askopenfilename(filetypes=[("G-code", "*.gcode")])
        if not file_path:
            return
        with open(file_path, 'r') as f:
            self.gcode_lines = [line.strip() for line in f if line.strip() and not line.startswith(';')]
        self.status.config(text=f"Загружено {len(self.gcode_lines)} строк G-code")

    def send_gcode(self):
        if not self.serial_conn or not self.gcode_lines:
            return

        total_lines = len(self.gcode_lines)
        self.progress['maximum'] = total_lines

        for i, line in enumerate(self.gcode_lines):
            self.serial_conn.write((line + '\n').encode())
            response = self.serial_conn.readline().decode().strip()
            self.status.config(text=f"Отправлено {i+1}/{total_lines}: {line}")
            self.progress['value'] = i+1
            self.root.update_idletasks()
            time.sleep(0.1)

        self.status.config(text="G-code отправлен!")
        messagebox.showinfo("Успех", "G-code успешно отправлен!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GCodeSender(root)
    root.mainloop()