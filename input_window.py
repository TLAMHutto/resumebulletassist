# input_window.py
import tkinter as tk
from tkinter import filedialog, Text

class TextProcessorWindow:
    def __init__(self, root):
        root.title("Text Processor")

        # Make the window resizable
        root.grid_rowconfigure(0, weight=1)  # Row 0 (text boxes) will expand
        root.grid_columnconfigure(0, weight=1)  # Column 0 (left text box) will expand
        root.grid_columnconfigure(1, weight=1)  # Column 1 (right text box) will expand

        # Create two text boxes (columns)
        self.left_text = Text(root, height=20, width=40)
        self.left_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.right_text = Text(root, height=20, width=40)
        self.right_text.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create the buttons
        upload_button = tk.Button(root, text="Upload", command=self.display_file)
        upload_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        process_button = tk.Button(root, text="Process", command=self.process_text)
        process_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        clear_button = tk.Button(root, text="Clear", command=self.clear_text)
        clear_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

    # Function to upload a file
    def upload_file(self):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(title="Select a file")
        return file_path

    # Function to display the file content in the left_text box
    def display_file(self):
        # Get the file path from upload_file()
        file_path = self.upload_file()
        if file_path:
            # Open and read the selected file
            with open(file_path, 'r') as file:
                content = file.read()
                # Display the content in the left_text box
                self.left_text.delete(1.0, tk.END)  # Clear the left text box
                self.left_text.insert(tk.END, content)  # Insert the file content

    # Function to process the text
    def process_text(self):
        input_text = self.left_text.get(1.0, tk.END)
        processed_text = input_text.upper()  # Example processing: convert to uppercase
        self.right_text.delete(1.0, tk.END)  # Clear the right text box
        self.right_text.insert(tk.END, processed_text)

    # Function to clear both text boxes
    def clear_text(self):
        self.left_text.delete(1.0, tk.END)
        self.right_text.delete(1.0, tk.END)
