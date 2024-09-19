# main.py
import tkinter as tk
from input_window import TextProcessorWindow

if __name__ == "__main__":
    root = tk.Tk()
    app = TextProcessorWindow(root)
    root.mainloop()
