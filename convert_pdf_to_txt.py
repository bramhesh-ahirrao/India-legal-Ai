import os
import re

try:
    import pdfplumber
except ImportError:
    print("pdfplumber is not installed. Please try: pip install pdfplumber")
    exit(1)

def convert_pdfs_to_text(input_dir="pdf_cases", output_dir="data/judgments", start_counter=51):
    """
    Scans the input_dir for PDFs. 
    Extracts text and saves to output_dir sequentially as case{N}.txt, 
    starting from start_counter, ensuring no files are overwritten.
    """
    # 1. Ensure output folder exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # 2. Verify input folder exists
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found.")
        return

    # Find all PDFs
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')])
    
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to convert.\n")

    current_counter = start_counter

    for pdf_filename in pdf_files:
        # 3. Find the next available filename (e.g. case51.txt) to avoid overwriting
        while True:
            out_filename = f"case{current_counter}.txt"
            out_path = os.path.join(output_dir, out_filename)
            if not os.path.exists(out_path):
                break
            current_counter += 1  # File exists, skip to next number
            
        pdf_path = os.path.join(input_dir, pdf_filename)
        
        try:
            print(f"Converting {pdf_filename} ", end="", flush=True)
            
            extracted_text_chunks = []
            
            # Extract text using pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text_chunks.append(text)
            
            # Combine all string pages into one
            final_text = "\n".join(extracted_text_chunks)
            
            # Save the file
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(final_text)
                
            print(f"→ {out_filename}")
            
            # Increment counter for the next PDF
            current_counter += 1
            
        except Exception as e:
            print(f"→ [ERROR] failed to process {pdf_filename}: {e}")

if __name__ == "__main__":
    # Ensure we use absolute paths relative to the script location
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    INPUT_DIR = os.path.join(project_root, "pdf_cases")
    OUTPUT_DIR = os.path.join(project_root, "data", "judgments")
    
    convert_pdfs_to_text(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, start_counter=51)
