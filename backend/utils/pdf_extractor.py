import os
import re
import traceback

try:
    import pdfplumber
except ImportError:
    print("pdfplumber is not installed. Please install it using: pip install pdfplumber")
    exit(1)

def clean_text(text):
    """
    Cleans the extracted text by removing common noise in Indian legal judgments.
    """
    if not text:
        return ""
        
    # Remove indian kanoon download header/footer
    text = re.sub(r'Downloaded from indiankanoon\.org(?:.*?)$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove standalone page numbers (e.g., "Page 1", "1", "- 1 -")
    text = re.sub(r'(?m)^\s*Page\s+\d+\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?m)^\s*-\s*\d+\s*-\s*$', '', text)
    text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
    
    # Remove repeated headers often found in judgments (customizable based on the specific PDFs)
    # Generic approach to collapse more than 3 newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def process_pdfs(input_dir="pdf_cases", output_dir="data/judgments"):
    """
    Scans input_dir for PDFs, extracts and cleans text, and saves to output_dir.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        print("Please create it and place your PDF judgments inside.")
        return

    # Scan for PDF files
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.\n")

    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        
        # Determine output filename (replace .pdf with .txt)
        base_name = os.path.splitext(filename)[0]
        txt_filename = f"{base_name}.txt"
        txt_path = os.path.join(output_dir, txt_filename)

        try:
            print(f"Processing {filename}...", end=" ", flush=True)
            
            full_text = []
            
            # Extract text using pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        full_text.append(extracted)
            
            # Join all pages with a newline
            combined_text = "\n".join(full_text)
            
            # Clean the text
            cleaned_text = clean_text(combined_text)
            
            # Save the result
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
                
            print(f"→ saved {txt_filename}")
            
        except Exception as e:
            print(f"→ Error processing {filename}: {str(e)}")
            # Uncomment for detailed debugging if a file keeps failing:
            # traceback.print_exc()

if __name__ == "__main__":
    # Assuming this script is run from the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    INPUT_DIR = os.path.join(project_root, "pdf_cases")
    OUTPUT_DIR = os.path.join(project_root, "data", "judgments")
    
    process_pdfs(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR)
