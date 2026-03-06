import os
import re
import json
import uuid
import tiktoken
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import voyageai

# Load environment variables from backend/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

# Configuration
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-cases")
VOYAGE_MODEL = "voyage-3-large"
EMBEDDING_DIM = 1024

# Initialize clients
if not VOYAGE_API_KEY or not PINECONE_API_KEY:
    print("Warning: VOYAGE_API_KEY or PINECONE_API_KEY not found in .env file.")

vo = voyageai.Client(api_key=VOYAGE_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(tokenizer.encode(text))

def chunk_text(text, chunk_size=400, overlap=50):
    """
    Splits text into chunks of chunk_size tokens with overlap, 
    attempting to preserve paragraph boundaries.
    """
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        para_tokens = count_tokens(para)
        
        if current_tokens + para_tokens <= chunk_size:
            current_chunk.append(para)
            current_tokens += para_tokens
        else:
            # If current_chunk is not empty, save it
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                
                # Create overlap: keep some paragraphs from the end
                # This is a bit complex with paragraph boundaries.
                # For simplicity, we'll just start a new chunk with the current paragraph
                # or find a better way. 
                # Let's try to keep at least 'overlap' tokens worth of text.
                overlap_chunk = []
                overlap_tokens = 0
                for p in reversed(current_chunk):
                    p_tokens = count_tokens(p)
                    if overlap_tokens + p_tokens <= overlap:
                        overlap_chunk.insert(0, p)
                        overlap_tokens += p_tokens
                    else:
                        break
                current_chunk = overlap_chunk
                current_tokens = overlap_tokens
            
            # If a single paragraph is larger than chunk_size, split it by sentences
            if para_tokens > chunk_size:
                sentences = re.split(r'(?<=[\.\!\?])\s+', para)
                for sent in sentences:
                    sent_tokens = count_tokens(sent)
                    if current_tokens + sent_tokens <= chunk_size:
                        current_chunk.append(sent)
                        current_tokens += sent_tokens
                    else:
                        if current_chunk:
                            chunks.append("\n\n".join(current_chunk))
                        # Start new chunk with current sentence
                        current_chunk = [sent]
                        current_tokens = sent_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
                
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks

def analyze_case_outcome(text):
    """
    Basic pattern detection to determine if a case was won or lost.
    """
    text_lower = text.lower()
    win_patterns = ["appeal is allowed", "appeal allowed", "suit decreed", "petition is allowed", "rule is made absolute"]
    loss_patterns = ["appeal is dismissed", "appeal dismissed", "suit dismissed", "petition is dismissed", "rule is discharged"]
    
    is_win = False
    is_loss = False
    
    # Check the last 30% of the text for the outcome
    tail_length = int(len(text_lower) * 0.3)
    tail_text = text_lower[-tail_length:] if tail_length > 0 else text_lower
    
    for pat in win_patterns:
        if pat in tail_text:
            is_win = True
            break
            
    for pat in loss_patterns:
        if pat in tail_text:
            is_loss = True
            break
            
    if is_win and not is_loss:
        return "Win"
    elif is_loss and not is_win:
        return "Loss"
    return "Unknown/Neutral"

def extract_metadata(filename, first_paragraph):
    """
    Extracts metadata from filename and first paragraph.
    Filename expected format: YYYY_COURT_ID.txt or caseXXX.txt
    """
    metadata = {
        "case_id": filename.replace(".txt", ""),
        "title": "Unknown Title",
        "court": "Unknown Court",
        "year": "Unknown",
        "outcome": "Unknown",
        "section": "Judgment"
    }
    
    # Try to parse filename
    parts = filename.replace(".txt", "").split('_')
    if len(parts) >= 1 and parts[0].isdigit():
        metadata["year"] = parts[0]
    
    if len(parts) >= 2:
        court_code = parts[1].upper()
        court_map = {
            "S": "Supreme Court of India",
            "D": "Delhi High Court",
            "M": "Madras High Court",
            "B": "Bombay High Court",
            "C": "Calcutta High Court",
            "A": "Allahabad High Court",
            "P": "Punjab & Haryana High Court",
            "G": "Gujarat High Court",
            "L": "Local/Lower Court"
        }
        metadata["court"] = court_map.get(court_code, f"{court_code} Court")

    # Try to extract title from first paragraph (often "Party A vs Party B")
    # Common legal formats: "A vs. B", "A v. B", "In re: A"
    title_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:v\.?|vs\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', first_paragraph)
    if title_match:
        metadata["title"] = title_match.group(1)
    else:
        # Check for "BETWEEN" ... "AND" or similar
        between_match = re.search(r'(?i)BETWEEN\s*:\s*(.*?)\n\s*AND\s*:\s*(.*?)\n', first_paragraph, re.DOTALL)
        if between_match:
            metadata["title"] = f"{between_match.group(1).strip()} v. {between_match.group(2).strip()}"
        else:
            # Fallback to first line if reasonably short and capitalized
            lines = [l.strip() for l in first_paragraph.split('\n') if l.strip()]
            if lines:
                metadata["title"] = lines[0][:100]
            
    return metadata

def setup_pinecone():
    """Checks if Pinecone index exists, creates it if not."""
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {PINECONE_INDEX_NAME}...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(PINECONE_INDEX_NAME)

def process_and_index():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_dir = os.path.join(project_root, "data", "judgments")
    
    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} not found.")
        return

    index = setup_pinecone()
    
    txt_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.txt')]
    print(f"Found {len(txt_files)} cases to process.")
    
    total_chunks = 0
    all_vectors = []
    
    for filename in sorted(txt_files):
        filepath = os.path.join(input_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            continue
            
        # Extract initial metadata
        case_meta = extract_metadata(filename, content[:1000])
        case_meta["outcome"] = analyze_case_outcome(content)
        
        # Chunk text
        chunks = chunk_text(content)
        print(f"Processing {filename}: {len(chunks)} chunks.")
        
        # Get embeddings in batches to be efficient
        # Voyage API supports batching
        chunk_embeddings = vo.embed(chunks, model=VOYAGE_MODEL, input_type="document").embeddings
        
        # Prepare vectors for Pinecone
        for i, (chunk, emb) in enumerate(zip(chunks, chunk_embeddings)):
            vector_id = f"{case_meta['case_id']}_chunk_{i}"
            metadata = case_meta.copy()
            metadata["text_snippet"] = chunk[:1000] # Safe snippet length
            
            all_vectors.append({
                "id": vector_id,
                "values": emb,
                "metadata": metadata
            })
            
            # Upsert in batches of 100
            if len(all_vectors) >= 100:
                index.upsert(vectors=all_vectors)
                total_chunks += len(all_vectors)
                all_vectors = []
                print(f"Indexed {total_chunks} chunks so far...")

    # Upsert remaining
    if all_vectors:
        index.upsert(vectors=all_vectors)
        total_chunks += len(all_vectors)
        
    print(f"Indexing complete! Total chunks indexed: {total_chunks}")

if __name__ == "__main__":
    process_and_index()
