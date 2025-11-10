import tkinter as tk
from tkinter import filedialog
import numpy as np

class GCodeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация G-code")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.root, text="Загрузить G-code", command=self.load_gcode).pack()

        self.lines = []
        self.pen_down = False

    def load_gcode(self):
        file_path = filedialog.askopenfilename(filetypes=[("G-code", "*.gcode")])
        if not file_path:
            return

        self.canvas.delete("all")
        self.lines = []
        x, y = 0, 0
        scale = 1

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('G0') or line.startswith('G1'):
                    new_x = x
                    new_y = y
                    if 'X' in line:
                        new_x = float(line.split('X')[1].split()[0]) * scale
                    if 'Y' in line:
                        new_y = float(line.split('Y')[1].split()[0]) * scale

                    if 'G0' in line:
                        self.pen_down = False
                    elif 'G1' in line:
                        self.pen_down = True

                    if self.pen_down:
                        self.canvas.create_line(x, y, new_x, new_y, fill="black", width=1)

                    x, y = new_x, new_y

if __name__ == "__main__":
    root = tk.Tk()
    app = GCodeVisualizer(root)
    root.mainloop()