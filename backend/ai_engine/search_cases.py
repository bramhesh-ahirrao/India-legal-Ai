import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone
import voyageai

# Load environment variables from backend/.env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

# Configuration
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "legal-cases")
VOYAGE_MODEL = "voyage-3-large"

# Initialize clients
vo = voyageai.Client(api_key=VOYAGE_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

def search_pinecone(query_text, top_k=10):
    """
    Search Pinecone index for semantically similar legal cases.
    """
    if not VOYAGE_API_KEY or not PINECONE_API_KEY:
        return {"error": "API keys not set. Please check .env file."}

    start_time = time.time()
    
    # Check if index exists
    if PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        return {"error": f"Index {PINECONE_INDEX_NAME} not found. Please run generate_embeddings.py first."}

    index = pc.Index(PINECONE_INDEX_NAME)
    
    # 1. Convert query to embedding
    try:
        query_embedding = vo.embed([query_text], model=VOYAGE_MODEL, input_type="query").embeddings[0]
    except Exception as e:
        return {"error": f"Embedding error: {str(e)}"}
    
    # 2. Search Pinecone
    try:
        search_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
    except Exception as e:
        return {"error": f"Pinecone query error: {str(e)}"}
    
    # 3. Process and group results by case_id
    grouped_results = {}
    
    for match in search_results["matches"]:
        metadata = match["metadata"]
        case_id = metadata["case_id"]
        similarity = match["score"]
        
        # If case already exists, keep the chunk with higher similarity
        if case_id not in grouped_results or similarity > grouped_results[case_id]["similarity"]:
            grouped_results[case_id] = {
                "case_id": case_id,
                "title": metadata.get("title", "Unknown"),
                "court": metadata.get("court", "Unknown"),
                "year": metadata.get("year", "Unknown"),
                "similarity": round(float(similarity), 3),
                "snippet": metadata.get("text_snippet", ""),
                "outcome": metadata.get("outcome", "Unknown")
            }
            
    # Convert dict to list and sort by similarity
    final_results = sorted(grouped_results.values(), key=lambda x: x["similarity"], reverse=True)
    
    elapsed = time.time() - start_time
    print(f"Search completed in {elapsed:.3f} seconds.")
    
    return final_results

if __name__ == "__main__":
    # Test search
    print("Testing search engine...")
    query = "property dispute between neighbors"
    results = search_pinecone(query)
    
    if "error" in results:
        print(f"Error: {results['error']}")
    else:
        for i, res in enumerate(results):
            print(f"{i+1}. {res['title']} ({res['year']}) | Score: {res['similarity']}")
            print(f"   Snippet: {res['snippet'][:150]}...")
            print("-" * 50)
