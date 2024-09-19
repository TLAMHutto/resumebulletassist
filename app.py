import subprocess
import os

def convert_markdown_to_pdf(input_md_path, output_pdf_path, pandoc_path):
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
        print("An error occurred:")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)

if __name__ == "__main__":
    # Define paths
    input_md_path = 'r.md'  # Replace with the path to your Markdown file
    output_pdf_path = 'resume.pdf'  # Replace with the desired output PDF path
    pandoc_path = r'C:\Users\keaton\pandoc-3.4\pandoc.exe'  # Path to Pandoc executable

    # Convert Markdown to PDF
    convert_markdown_to_pdf(input_md_path, output_pdf_path, pandoc_path)
