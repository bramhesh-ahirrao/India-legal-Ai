import os
import sys

# Simply import and run the backend implementation
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from ai_engine.search_cases import load_index_and_metadata, search_cases

if __name__ == "__main__":
    print("-" * 50)
    print("India Legal AI - Semantic Search Engine")
    print("-" * 50)
    
    # 1. Load the FAISS index and metadata
    idx, meta, mdl = load_index_and_metadata()
    
    # Run the interactive loop
    while True:
        try:
            user_query = input("\nEnter legal search query (or 'exit' to quit): ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("Shutting down the Legal AI engine. Goodbye!")
                break
                
            if not user_query:
                continue
                
            search_cases(user_query, idx, meta, mdl, top_k=5)
            
        except KeyboardInterrupt:
            print("\nShutting down the Legal AI engine. Goodbye!")
            break
