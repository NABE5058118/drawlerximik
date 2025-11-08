import tkinter as tk
from gui.app import AdvancedCNCApp

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedCNCApp(root)
    root.mainloop()