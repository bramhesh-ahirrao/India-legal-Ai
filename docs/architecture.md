# India Legal AI Architecture

## ⚖️ Project Overview
**India Legal AI** is a cutting-edge platform designed to analyze, search, and simplify Indian legal judgments using modern AI. The goal is to provide lawyers, researchers, and citizens with intelligent tools for legal data analysis.

---

## 🏗️ System Components

### 1. Backend (`/backend`)
A Python-based API server that handles judgment processing, AI query processing, and data retrieval.
- **`app.py`**: Entry point for the API server.
- **`routes/`**: API endpoint definitions (e.g., judgments, search, AI chat).
- **`ai_engine/`**: Core AI logic, including search and synthesis.
- **`utils/`**: Helper functions for text processing, file parsing, and formatting.

### 2. Frontend (`/frontend`)
The user interface, built using React and modern CSS for a premium, fast experience.
- **`src/components/`**: Reusable UI components (Sidebar, SearchBar, JudgmentCard).
- **`src/pages/`**: Main application views (Dashboard, SearchResults, CaseAnalysis).

### 3. Data Storage (`/data`)
Local storage for raw and processed legal documents.
- **`judgments/`**: Folder for storing legal texts in format like PDF, TXT, or JSON.

### 4. AI Models (`/ai_models`)
Pre-trained models and local data for machine learning.
- **`embeddings/`**: Vectorized representations of judgments for fast retrieval.

---

## 🛠️ Tech Stack
- **Backend**: Python (Flask/FastAPI), Sentence-Transformers, OpenAI/Anthropic SDKs.
- **Frontend**: React, Tailwind CSS, Framer Motion (for animations).
- **Storage**: Vector Database (Chroma/FAISS) for embeddings, JSON for metadata.

---

## 🔜 Phase 1 Goals
- [ ] Initialize the project structure.
- [ ] Implement a basic search function for Indian judgments.
- [ ] Create a modern, responsive UI for judgment exploration.
- [ ] Set up basic RAG (Retrieval-Augmented Generation) for legal queries.
