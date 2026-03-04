from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Basic configuration
DATA_DIR = os.path.join(os.getcwd(), '..', 'data', 'judgments')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "service": "India Legal AI Backend",
        "version": "1.0.0"
    })

@app.route('/api/search', methods=['POST'])
def search_judgments():
    """Endpoint for searching judgments."""
    data = request.json
    query = data.get('query', '')
    
    # Placeholder for AI search logic
    # In Phase 1, we will integrate vector search and embeddings.
    return jsonify({
        "query": query,
        "results": [
            {
                "id": 1,
                "title": "Kesavananda Bharati v. State of Kerala",
                "court": "Supreme Court of India",
                "year": "1973",
                "summary": "Basic structure doctrine established."
            },
            {
                "id": 2,
                "title": "Maneka Gandhi v. Union of India",
                "court": "Supreme Court of India",
                "year": "1978",
                "summary": "Right to personal liberty and due process."
            }
        ]
    })

if __name__ == '__main__':
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    
    app.run(debug=True, port=5000)
