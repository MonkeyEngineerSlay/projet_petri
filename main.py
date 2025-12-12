# main.py
import tkinter as tk
from interface import PetriApp

if __name__ == "__main__":
    root = tk.Tk()
    app = PetriApp(root)
    root.mainloop()