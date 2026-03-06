import fitz # PyMuPDF
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extracts text from the first 20 pages of a PDF file using PyMuPDF.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        doc = fitz.open(file_path)
        page_count = len(doc)
        
        logger.info(f"PDF uploaded: {os.path.basename(file_path)}")
        logger.info(f"Pages detected: {page_count}")
        
        # Limit extraction to first 20 pages for demo performance
        extraction_limit = min(page_count, 20)
        
        full_text = []
        for i in range(extraction_limit):
            page = doc.load_page(i)
            text = page.get_text()
            if text:
                full_text.append(text)
        
        doc.close()
        
        logger.info("Text extraction completed")
        
        return {
            "filename": os.path.basename(file_path),
            "pages": page_count,
            "text": "\n".join(full_text)
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise e

if __name__ == "__main__":
    # Test script
    test_file = "pdf_cases/A2Z_Infraservices_Ltd_vs_Union_Of_India_And_3_Ors_on_25_April_2018.PDF"
    if os.path.exists(test_file):
        result = extract_text_from_pdf(test_file)
        print(f"Extraction successful: {result['filename']}, Pages: {result['pages']}")
    else:
        print("Sample file not found for testing.")
