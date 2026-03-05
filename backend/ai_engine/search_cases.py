import os
import json
import time
import numpy as np

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Missing dependencies. Please install: pip install faiss-cpu sentence-transformers")
    exit(1)

def load_index_and_metadata():
    """
    Loads the FAISS index and metadata specifically from ai_models/embeddings/
    Returns (index, metadata, model)
    """
    # Assuming script is in backend/ai_engine/ or root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.exists(os.path.join(project_root, "ai_models", "embeddings")):
        project_root = os.path.dirname(os.path.abspath(__file__))
        
    embed_dir = os.path.join(project_root, "ai_models", "embeddings")
    faiss_index_file = os.path.join(embed_dir, "case_index.faiss")
    metadata_file = os.path.join(embed_dir, "cases_metadata.json")

    # 1 & 2: Load FAISS index and metadata
    if not os.path.exists(faiss_index_file) or not os.path.exists(metadata_file):
        print(f"Error: Could not find FAISS index or metadata in {embed_dir}")
        print("Please run generate_embeddings.py first.")
        exit(1)

    index = faiss.read_index(faiss_index_file)
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 3: Load the embedding model
    print("Loading Sentence Transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("AI Model & Legal Database successfully loaded!\n")
    
    return index, metadata, model

def search_cases(query, index, metadata, model, top_k=5):
    """
    Performs quick semantic search using FAISS.
    """
    start_time = time.time()
    
    # 5. Convert query to embedding
    query_vector = model.encode([query], convert_to_numpy=True)
    
    # 6. Search the FAISS index
    distances, indices = index.search(query_vector, top_k)
    
    elapsed = time.time() - start_time

    print(f"\nTop {top_k} Similar Legal Cases (Found in {elapsed:.3f} seconds):")
    print("-" * 60)
    
    # 7 & 8. Return results matching output requirements
    for i in range(top_k):
        idx = indices[0][i]
        dist = distances[0][i]
        
        # Sentence Transformer 'all-MiniLM-L6-v2' outputs normalized vectors.
        # In FAISS IndexFlatL2, distance is Euclidean squared (L2^2).
        # Cosine Similarity = 1 - (L2_distance / 2)
        similarity = 1.0 - (dist / 2.0)
        
        # Guard against minor floating point anomalies
        similarity = max(0.0, min(1.0, similarity))
        
        file_meta = metadata[idx]
        filename = file_meta.get("filename", "Unknown")
        full_text = file_meta.get("full_text", "")
        
        # Get preview of first 400 characters and clean newlines
        preview = full_text[:400].replace('\n', ' ')
        
        print(f"{i + 1}. {filename}")
        print(f"   Similarity: {similarity:.2f}")
        print(f"   Preview:\n   \"{preview}...\"\n")

if __name__ == "__main__":
    print("-" * 50)
    print("India Legal AI - Semantic Search Engine")
    print("-" * 50)
    
    # Initialization
    idx, meta, mdl = load_index_and_metadata()
    
    # 4 & 9. Search loop via terminal
    while True:
        user_query = input("Enter legal search query (or 'exit' to quit): ").strip()
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            print("Shutting down the Legal AI engine. Goodbye!")
            break
            
        if not user_query:
            continue
            
        search_cases(user_query, idx, meta, mdl, top_k=5)
