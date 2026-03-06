import os
import sys
from dotenv import load_dotenv

# Ensure we can import from the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

import anthropic
import voyageai
from pinecone import Pinecone

def test_claude():
    print("\n--- Testing Claude API ---")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or "your_anthropic_api_key_here" in api_key:
        print("Skipping Claude test: ANTHROPIC_API_KEY is not set.")
        return False
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say hello world"}]
        )
        print(f"Claude Response: {message.content[0].text}")
        return True
    except Exception as e:
        print(f"Claude Error: {str(e)}")
        return False

def test_voyage():
    print("\n--- Testing Voyage AI ---")
    api_key = os.getenv("VOYAGE_API_KEY")
    if not api_key or "your_voyage_api_key_here" in api_key:
        print("Skipping Voyage test: VOYAGE_API_KEY is not set.")
        return False
        
    try:
        vo = voyageai.Client(api_key=api_key)
        emb = vo.embed(["Legal AI"], model="voyage-3-large", input_type="query").embeddings[0]
        print(f"Voyage Embedding Length: {len(emb)}")
        return True
    except Exception as e:
        print(f"Voyage Error: {str(e)}")
        return False

def test_pinecone():
    print("\n--- Testing Pinecone ---")
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "legal-cases")
    if not api_key or "your_pinecone_api_key_here" in api_key:
        print("Skipping Pinecone test: PINECONE_API_KEY is not set.")
        return False
        
    try:
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes().names()
        print(f"Pinecone Indexes: {indexes}")
        return True
    except Exception as e:
        print(f"Pinecone Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_claude()
    test_voyage()
    test_pinecone()
