import os
import json
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Missing dependencies. Please install: pip install faiss-cpu sentence-transformers")
    exit(1)

def build_vector_index(force_recreate=False):
    """
    Reads all parsed judgment texts, generates embeddings using Sentence Transformers, 
    and builds a FAISS index for semantic similarity search.
    """
    # Define paths
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # If placed in root, adjust root directory resolution
    if not os.path.exists(os.path.join(project_root, "data", "judgments")):
        project_root = os.path.dirname(os.path.abspath(__file__))

    input_dir = os.path.join(project_root, "data", "judgments")
    output_dir = os.path.join(project_root, "ai_models", "embeddings")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Output file paths
    embeddings_file = os.path.join(output_dir, "embeddings.npy")
    faiss_index_file = os.path.join(output_dir, "case_index.faiss")
    metadata_file = os.path.join(output_dir, "cases_metadata.json")
    
    # Check if files already exist
    if not force_recreate and os.path.exists(faiss_index_file) and os.path.exists(metadata_file):
        print("FAISS index and metadata already exist. Skipping creation.")
        print("To recreate the index, pass force_recreate=True.")
        return

    # 1. Scan the folder `data/judgments`
    if not os.path.exists(input_dir):
        print(f"Data directory '{input_dir}' not found.")
        return
        
    txt_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.txt')]
    if not txt_files:
        print(f"No text files found in '{input_dir}'.")
        return
        
    documents = []
    metadata = []
    
    # 2. Load every .txt file and read its content (ignoring .gitkeep and other non-txt files)
    print("Reading text files...")
    for filename in sorted(txt_files):
        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text_content = file.read().strip()
                if text_content:
                    documents.append(text_content)
                    metadata.append({
                        "filename": filename,
                        "full_text": text_content
                    })
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    print(f"Loaded {len(documents)} cases")

    # 3. Generate embeddings for each case
    print("Loading Sentence Transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating embeddings. This may take a few minutes depending on document sizes...")
    # Generating embeddings
    embeddings = model.encode(documents, show_progress_bar=True, convert_to_numpy=True)
    print("Embeddings generated")

    # 4. Store embeddings in a NumPy array and save
    np.save(embeddings_file, embeddings)
    
    # 5. Save metadata containing filename and full text
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    # 6. Build a FAISS index from these embeddings
    # all-MiniLM-L6-v2 produces 384-dimensional embeddings
    dimension = embeddings.shape[1]
    
    # Using L2 distance standard IndexFlatL2
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(embeddings)
    
    # 7. Save the FAISS index
    faiss.write_index(index, faiss_index_file)
    print("FAISS index created")
    
    print(f"Index successfully saved at: {output_dir}")

if __name__ == "__main__":
    build_vector_index(force_recreate=False)
