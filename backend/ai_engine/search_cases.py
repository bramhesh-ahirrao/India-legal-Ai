import os
import json
import time
import re
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

def analyze_case_outcome(text):
    """
    Basic pattern detection to determine if a case was won or lost
    and extract the winning argument.
    """
    text_lower = text.lower()
    
    # Simple keyword tracking for win/loss at the end of judgements
    win_patterns = ["appeal is allowed", "appeal allowed", "suit decreed", "petition is allowed", "rule is made absolute"]
    loss_patterns = ["appeal is dismissed", "appeal dismissed", "suit dismissed", "petition is dismissed", "rule is discharged"]
    
    is_win = False
    is_loss = False
    
    # We generally check the last 20% of the text for the outcome
    tail_length = int(len(text_lower) * 0.2)
    tail_text = text_lower[-tail_length:] if tail_length > 0 else text_lower
    
    for pat in win_patterns:
        if pat in tail_text:
            is_win = True
            break
            
    for pat in loss_patterns:
        if pat in tail_text:
            is_loss = True
            break
            
    # If both or neither, consider it neutral or unresolved context
    outcome = "Unknown/Neutral"
    if is_win and not is_loss:
        outcome = "Win"
    elif is_loss and not is_win:
        outcome = "Loss"
        
    # Extract basic pattern argument (sentence containing 'held that' or 'therefore')
    argument = "No specific winning argument pattern detected."
    sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
    for s in reversed(sentences):
        s_lower = s.lower()
        if "held that" in s_lower or "therefore" in s_lower or "consequently" in s_lower:
            # Avoid too short or too long sentences
            if 20 < len(s) < 300:
                argument = s.strip()
                break
                
    return outcome, argument

def search_cases(query, index, metadata, model, top_k=10):
    """
    Performs quick semantic search using FAISS, returning top 10 matches.
    Includes win-rate calculation and strategy generation.
    """
    start_time = time.time()
    
    # Convert query to embedding
    query_vector = model.encode([query], convert_to_numpy=True)
    
    # Search the FAISS index
    distances, indices = index.search(query_vector, top_k)
    elapsed = time.time() - start_time

    print(f"\nTop {top_k} Similar Legal Cases (Found in {elapsed:.3f} seconds):")
    print("=" * 70)
    
    total_wins = 0
    total_losses = 0
    winning_arguments = []
    
    # Return results matching output requirements
    for i in range(top_k):
        idx = indices[0][i]
        dist = distances[0][i]
        
        # Calculate Cosine Similarity from L2 squared distance
        similarity = 1.0 - (dist / 2.0)
        similarity = max(0.0, min(1.0, similarity))
        
        file_meta = metadata[idx]
        filename = file_meta.get("filename", "Unknown")
        full_text = file_meta.get("full_text", "")
        
        # Calculate Win/Loss and extract arguments
        outcome, argument = analyze_case_outcome(full_text)
        
        if outcome == "Win":
            total_wins += 1
            if argument != "No specific winning argument pattern detected.":
                winning_arguments.append(argument)
        elif outcome == "Loss":
            total_losses += 1
        
        # Get preview of first 400 characters and clean newlines
        preview = full_text[:200].replace('\n', ' ')
        
        print(f"{i + 1}. {filename} | Similarity: {similarity:.2f} | Outcome: {outcome}")
        print(f"   Preview: \"{preview}...\"")
        print("-" * 70)
        
    # Calculate overarching Strategy and Win-Rate
    known_outcomes = total_wins + total_losses
    win_rate = (total_wins / known_outcomes * 100) if known_outcomes > 0 else 0
    
    print("\n" + "=" * 70)
    print(f"ANALYTICS & STRATEGY ENGINE")
    print("=" * 70)
    print(f"Total Top 10 Analyzed: {top_k}")
    print(f"Historical Appeals/Suits Outcome: {total_wins} Wins, {total_losses} Losses")
    print(f"Estimated Win-Rate for this Query's typical fact pattern: {win_rate:.1f}%")
    print("\nSuggested Winning Patterns / Key Arguments based on successful similar cases:")
    
    if winning_arguments:
        for j, arg in enumerate(set(winning_arguments[:3])):  # Show top 3 unique
            print(f"  * {arg}")
    else:
        print("  * Insufficient clear winning patterns extracted. Deeper analysis required.")
        
    print("=" * 70 + "\n")

if __name__ == "__main__":
    print("-" * 50)
    print("India Legal AI - Semantic Search Engine")
    print("-" * 50)
    
    # Initialization
    idx, meta, mdl = load_index_and_metadata()
    
    # Search loop
    while True:
        user_query = input("Enter legal search query (or 'exit' to quit): ").strip()
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            print("Shutting down the Legal AI engine. Goodbye!")
            break
            
        if not user_query:
            continue
            
        search_cases(user_query, idx, meta, mdl, top_k=10)
