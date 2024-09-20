import tkinter as tk
from tkinter import filedialog, messagebox, Text, ttk
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import PyPDF2
import io
import ollama
import os
import tempfile
import subprocess
import chardet
class PDFPreviewWindow:
    def __init__(self, master):
        self.master = master
        self.pdf_window = tk.Toplevel(master)
        self.pdf_window.title("PDF Preview")
        self.pdf_window.geometry("800x600")

        self.canvas = tk.Canvas(self.pdf_window)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.select_button = tk.Button(self.pdf_window, text="Select PDF", command=self.select_pdf)
        self.select_button.pack(pady=10)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.display_pdf(file_path)

    def display_pdf(self, file_path):
        try:
            # Convert the first page of the PDF to an image
            images = convert_from_path(file_path, first_page=1, last_page=1)
            
            if images:
                img = images[0]
                
                # Resize image to fit the canvas
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                img.thumbnail((canvas_width, canvas_height))
                
                photo = ImageTk.PhotoImage(img)
                
                # Clear previous content and display the new image
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas.image = photo  # Keep a reference
            else:
                messagebox.showinfo("Info", "Unable to render the PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

class TextProcessorWindow:
    def __init__(self, root):
        self.root = root
        root.title("Text Processor")

        # Main frame setup remains the same
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # PanedWindow setup remains the same
        self.main_paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        self.top_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.top_paned)

        self.bottom_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.bottom_paned)

        # Create text widgets
        self.job_desc_text = Text(self.top_paned, height=5, width=40)
        self.ai_desc_text = Text(self.top_paned, height=5, width=40)
        self.md_text = Text(self.bottom_paned, height=20, width=40)

        # Add text widgets to PanedWindows
        self.top_paned.add(self.job_desc_text)
        self.top_paned.add(self.ai_desc_text)
        self.bottom_paned.add(self.md_text)

        # Create a frame for the PDF status label
        pdf_status_frame = ttk.Frame(self.bottom_paned)
        self.bottom_paned.add(pdf_status_frame)

        # Create the PDF status label
        self.pdf_status_label = ttk.Label(pdf_status_frame, text="PDF Status: Not generated", wraplength=300)
        self.pdf_status_label.pack(pady=10, padx=10)

        # Add placeholders
        self.add_placeholder(self.job_desc_text, "Enter job description here and press enter...")
        self.add_placeholder(self.ai_desc_text, "Model output")
        self.add_placeholder(self.md_text, "Markdown Text")

        # Button frame and buttons remain the same
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        upload_button = ttk.Button(button_frame, text="Upload", command=self.display_file)
        upload_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        process_button = ttk.Button(button_frame, text="Process", command=self.process_text)
        process_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.preview_button = ttk.Button(button_frame, text="Preview PDF", command=self.preview_pdf)
        self.preview_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_text)
        clear_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # Rest of the initialization remains the same
        self.job_desc_text.bind("<Return>", self.on_enter_pressed)

        dropdown_frame = ttk.Frame(main_frame)
        dropdown_frame.pack(fill=tk.X, padx=10, pady=10)

        self.model_var = tk.StringVar(root)
        self.model_dropdown = ttk.Combobox(dropdown_frame, textvariable=self.model_var, state="readonly")
        self.model_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        refresh_button = ttk.Button(dropdown_frame, text="Refresh Models", command=self.update_model_list)
        refresh_button.pack(side=tk.LEFT, padx=(5, 0))

        self.update_model_list()

    def preview_pdf(self):
        PDFPreviewWindow(self.root)
    
    def add_placeholder(self, text_widget, placeholder_text):
        text_widget.insert(1.0, placeholder_text)
        text_widget.config(fg="grey")
        text_widget.bind("<FocusIn>", lambda event: self.on_focus_in(event, placeholder_text))
        text_widget.bind("<FocusOut>", lambda event: self.on_focus_out(event, placeholder_text))

    def on_focus_in(self, event, placeholder_text):
        text_widget = event.widget
        if text_widget.get(1.0, tk.END).strip() == placeholder_text:
            text_widget.delete(1.0, tk.END)
            text_widget.config(fg="black")

    def on_focus_out(self, event, placeholder_text):
        text_widget = event.widget
        if not text_widget.get(1.0, tk.END).strip():
            text_widget.insert(1.0, placeholder_text)
            text_widget.config(fg="grey")

    def update_model_list(self):
        try:
            models = ollama.list()
            model_names = [model['name'] for model in models['models']]
            self.model_dropdown['values'] = model_names
            if model_names:
                self.model_var.set(model_names[0])
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            self.model_dropdown['values'] = ["Error fetching models"]
            self.model_var.set("Error fetching models")

    def send_message(self):
        job_desc = self.job_desc_text.get("1.0", "end-1c").strip()
        

        model = self.model_var.get()
        prompt = """Based on the following job description, generate 10 concise, impactful bullet points that I can use in my resume. Each bullet point should:
        1. Start with a strong action verb
        2. Highlight a relevant skill or achievement
        3. Be tailored to the job requirements
        4. Be quantifiable where possible
        5. Be no longer than one line each

        Here's the job description:

        """ + job_desc

        try:
            response = ollama.chat(model=model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])

            ai_message = response['message']['content']
            self.ai_desc_text.delete(1.0, tk.END)
            self.ai_desc_text.insert(tk.END, ai_message)
        except Exception as e:
            self.ai_desc_text.delete(1.0, tk.END)
            self.ai_desc_text.insert(tk.END, f"Error: Failed to get response from {model}. {str(e)}")

    def on_enter_pressed(self, event):
        self.send_message()
        return 'break'
        
        
    # Function to upload a file
    def upload_file(self):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(title="Select a file")
        return file_path

    # Function to display the file content in the md_text box
    def display_file(self):
        file_path = self.upload_file()
        if file_path:
            try:
                # First, try to detect the file encoding
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']

                # Now, try to read the file with the detected encoding
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                
                # Display the content in the md_text box
                self.md_text.delete(1.0, tk.END)  # Clear the text box
                self.md_text.insert(tk.END, content)  # Insert the file content
            except UnicodeDecodeError:
                # If the detected encoding fails, try with 'utf-8' ignoring errors
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    self.md_text.delete(1.0, tk.END)
                    self.md_text.insert(tk.END, content)
                except Exception as e:
                    self.md_text.delete(1.0, tk.END)
                    self.md_text.insert(tk.END, f"Error reading file: {str(e)}")
            except Exception as e:
                self.md_text.delete(1.0, tk.END)
                self.md_text.insert(tk.END, f"Error reading file: {str(e)}")

    # Function to process the text and convert it using Pandoc
    def process_text(self):
    # Get the Markdown content from the md_text box
        markdown_content = self.md_text.get(1.0, tk.END)

        # Function to remove non-UTF-8 characters
        def remove_non_utf8_chars(text):
            return text.encode('utf-8', 'ignore').decode('utf-8')

        # Clean the markdown content by removing non-UTF-8 characters
        cleaned_markdown_content = remove_non_utf8_chars(markdown_content)

        # Temporary Markdown file path
        temp_md_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md").name

        # Write the cleaned Markdown content to a temporary file
        with open(temp_md_file, 'w', encoding='utf-8') as md_file:
            md_file.write(cleaned_markdown_content)

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
            self.pdf_status_label.config(text=f"PDF generated successfully!\nSaved to: {output_pdf_path}")
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
        self.md_text.delete(1.0, tk.END)
        self.job_desc_text.delete(1.0, tk.END)
        self.ai_desc_text.delete(1.0, tk.END)
        self.pdf_status_label.config(text="PDF Status: Not generated")

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
