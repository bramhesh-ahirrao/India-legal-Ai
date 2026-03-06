from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import logging
from dotenv import load_dotenv

# Load all logic from ai_engine and utils
# Check if current directory is correct for imports
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from ai_engine.search_cases import search_pinecone
from utils.pdf_extractor import extract_text_from_pdf

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="India Legal AI Platform")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {"message": "Legal AI Backend Running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """PDF Upload and Text Extraction endpoint."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"PDF uploaded: {file.filename}")
        extraction_result = extract_text_from_pdf(file_path)
            
        return {
            "filename": extraction_result["filename"],
            "pages": extraction_result["pages"],
            "text": extraction_result["text"]
        }
        
    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/search")
@app.post("/api/search")
async def search_judgments(request_data: dict):
    """Semantic Search endpoint using Voyage AI and Pinecone."""
    if 'query' not in request_data:
        raise HTTPException(status_code=400, detail="No query provided.")
        
    query = request_data['query']
    results = search_pinecone(query)
    
    if isinstance(results, dict) and 'error' in results:
        raise HTTPException(status_code=500, detail=results['error'])
        
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
