import tkinter as tk
from tkinter import filedialog, Text
import subprocess
import os
import tempfile

class TextProcessorWindow:
    def __init__(self, root):
        root.title("Text Processor")

        # Placeholder text for text boxes
        self.job_desc_pd = "Enter job description here..."
        self.ai_desc_pd = "AI outputs here..."
        self.md_pd = "Enter Markdown or upload here..."
        self.pdf_pd = "Processed output status will appear here..."

        # Make the window resizable
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Create two new text boxes (top row) with placeholders
        self.job_desc_text = Text(root, height=5, width=40)
        self.job_desc_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.add_placeholder(self.job_desc_text, self.job_desc_pd)

        self.ai_desc_text = Text(root, height=5, width=40)
        self.ai_desc_text.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.add_placeholder(self.ai_desc_text, self.ai_desc_pd)

        # Create two existing text boxes (bottom row) with placeholders
        self.md_text = Text(root, height=20, width=40)
        self.md_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.add_placeholder(self.md_text, self.md_pd)

        self.pdf_text = Text(root, height=20, width=40)
        self.pdf_text.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.add_placeholder(self.pdf_text, self.pdf_pd)

        # Create the buttons
        upload_button = tk.Button(root, text="Upload", command=self.display_file)
        upload_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        process_button = tk.Button(root, text="Process", command=self.process_text)
        process_button.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        clear_button = tk.Button(root, text="Clear", command=self.clear_text)
        clear_button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    # Function to add placeholder functionality to Text widget
    def add_placeholder(self, text_widget, placeholder_text):
        # Insert placeholder text
        text_widget.insert(1.0, placeholder_text)
        text_widget.config(fg="grey")

        # Bind focus-in event to remove placeholder
        text_widget.bind("<FocusIn>", lambda event: self.on_focus_in(event, placeholder_text))

        # Bind focus-out event to add placeholder back if empty
        text_widget.bind("<FocusOut>", lambda event: self.on_focus_out(event, placeholder_text))

    # Focus-in event handler to clear placeholder
    def on_focus_in(self, event, placeholder_text):
        text_widget = event.widget
        if text_widget.get(1.0, tk.END).strip() == placeholder_text:
            text_widget.delete(1.0, tk.END)
            text_widget.config(fg="black")

    # Focus-out event handler to add placeholder if the box is empty
    def on_focus_out(self, event, placeholder_text):
        text_widget = event.widget
        if not text_widget.get(1.0, tk.END).strip():
            text_widget.insert(1.0, placeholder_text)
            text_widget.config(fg="grey")

    # Function to upload a file
    def upload_file(self):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(title="Select a file")
        return file_path

    # Function to display the file content in the md_text box
    def display_file(self):
        # Get the file path from upload_file()
        file_path = self.upload_file()
        if file_path:
            # Open and read the selected file
            with open(file_path, 'r') as file:
                content = file.read()
                # Display the content in the md_text box
                self.md_text.delete(1.0, tk.END)  # Clear the left text box
                self.md_text.insert(tk.END, content)  # Insert the file content

    # Function to process the text and convert it using Pandoc
    def process_text(self):
        # Get the Markdown content from the md_text box
        markdown_content = self.md_text.get(1.0, tk.END)

        # Temporary Markdown file path
        temp_md_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md").name

        # Write the Markdown content to a temporary file
        with open(temp_md_file, 'w') as md_file:
            md_file.write(markdown_content)

        # Ask the user where to save the PDF
        output_pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF as"
        )

        # If the user doesn't provide a path, exit
        if not output_pdf_path:
            self.pdf_text.delete(1.0, tk.END)
            self.pdf_text.insert(tk.END, "PDF saving canceled.")
            return

        # Convert the Markdown file to PDF
        pandoc_path = r'C:\Users\keaton\pandoc-3.4\pandoc.exe'  # Path to Pandoc executable
        try:
            self.convert_markdown_to_pdf(temp_md_file, output_pdf_path, pandoc_path)
            # If successful, display success message in pdf_text
            self.pdf_text.delete(1.0, tk.END)
            self.pdf_text.insert(tk.END, f"PDF generated successfully!\nSaved to: {output_pdf_path}")
        except Exception as e:
            # Display error in pdf_text if conversion fails
            self.pdf_text.delete(1.0, tk.END)
            self.pdf_text.insert(tk.END, f"Error occurred: {str(e)}")

        # Clean up temporary Markdown file
        os.remove(temp_md_file)

    # Function to clear both text boxes
    def clear_text(self):
        self.md_text.delete(1.0, tk.END)
        self.pdf_text.delete(1.0, tk.END)
        self.job_desc_text.delete(1.0, tk.END)  # Clear the new top-left text box
        self.ai_desc_text.delete(1.0, tk.END)  # Clear the new top-right text box

    # Function to convert markdown to PDF using Pandoc
    def convert_markdown_to_pdf(self, input_md_path, output_pdf_path, pandoc_path):
        # Construct the command
        command = [
            pandoc_path,  # Path to the Pandoc executable
            input_md_path,  # Input Markdown file
            '-o', output_pdf_path  # Output PDF file
        ]

        # Run the command
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print("PDF created successfully.")
            print("stdout:", result.stdout)
            print("stderr:", result.stderr)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Pandoc failed. stdout: {e.stdout}, stderr: {e.stderr}")
