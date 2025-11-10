import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import time
import csv
from datetime import datetime
from calibration.conversion_utils import mm_to_steps

class CalibrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Калибровка: мм ↔ шаги")
        self.root.geometry("800x600")
        self.serial_conn = None
        self.points_mm = []
        self.points_steps = []

        self.setup_ui()

    def setup_ui(self):
        # Порт и подключение
        conn_frame = tk.Frame(self.root)
        conn_frame.pack(pady=10)

        tk.Label(conn_frame, text="COM-порт:").grid(row=0, column=0)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1)
        tk.Button(conn_frame, text="Обновить", command=self.update_ports).grid(row=0, column=2)
        tk.Button(conn_frame, text="Подключиться", command=self.connect).grid(row=0, column=3)

        # Управление
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Координаты (мм):").grid(row=0, column=0)
        self.x_var = tk.DoubleVar(value=0)
        self.y_var = tk.DoubleVar(value=0)
        tk.Entry(control_frame, textvariable=self.x_var, width=10).grid(row=0, column=1)
        tk.Entry(control_frame, textvariable=self.y_var, width=10).grid(row=0, column=2)
        tk.Button(control_frame, text="Двигать", command=self.move_to).grid(row=0, column=3)

        tk.Button(control_frame, text="Сохранить точку", command=self.save_point).grid(row=1, column=0, columnspan=4, pady=10)

        # Таблица точек
        table_frame = tk.Frame(self.root)
        table_frame.pack(pady=10)

        self.tree = ttk.Treeview(table_frame, columns=("mm", "steps"), show="headings")
        self.tree.heading("mm", text="мм (X, Y)")
        self.tree.heading("steps", text="Шаги (X, Y)")
        self.tree.pack()

        # Сохранить CSV
        tk.Button(self.root, text="Сохранить CSV", command=self.save_csv).pack(pady=10)

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
            self.serial_conn = serial.Serial(port, 115200, timeout=1)
            messagebox.showinfo("Успех", f"Подключено к {port}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")

    def move_to(self):
        if not self.serial_conn:
            messagebox.showerror("Ошибка", "Не подключено к Arduino")
            return
        x = self.x_var.get()
        y = self.y_var.get()
        steps_x = mm_to_steps(x, 'X')
        steps_y = mm_to_steps(y, 'Y')
        cmd = f"G0 X{steps_x} Y{steps_y}\n"
        self.serial_conn.write(cmd.encode())
        time.sleep(0.1)

    def save_point(self):
        x_mm = self.x_var.get()
        y_mm = self.y_var.get()
        # Предположим, что текущие шаги можно получить из Arduino
        # В реальности это зависит от текущего положения
        steps_x = mm_to_steps(x_mm, 'X')
        steps_y = mm_to_steps(y_mm, 'Y')
        self.points_mm.append((x_mm, y_mm))
        self.points_steps.append((steps_x, steps_y))
        self.tree.insert("", "end", values=[f"({x_mm}, {y_mm})", f"({steps_x}, {steps_y})"])

    def save_csv(self):
        if not self.points_mm:
            messagebox.showwarning("Внимание", "Нет точек для сохранения")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filename:
            return
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["mm_x", "mm_y", "steps_x", "steps_y"])
            for mm, steps in zip(self.points_mm, self.points_steps):
                writer.writerow([mm[0], mm[1], steps[0], steps[1]])
        messagebox.showinfo("Успех", f"Точки сохранены в {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationGUI(root)
    root.mainloop()