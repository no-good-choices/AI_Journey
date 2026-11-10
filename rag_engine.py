import os
import json
import requests
import numpy as np
from pypdf import PdfReader

# Ensure your local terminal environment has your key set, e.g., export GEMINI_API_KEY="your-key"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def extract_chunks_from_pdf(pdf_path, chunk_size=500, overlap=100):
    """Reads a PDF and slices its text into overlapping character chunks."""
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find PDF at {pdf_path}")
        return []
    
    print(f"📖 Reading document: {pdf_path}")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    chunks = []
    start = 0
    while start < len(full_text):
        end = start + chunk_size
        chunks.append(full_text[start:end].strip())
        start += (chunk_size - overlap)
        
    print(f"✅ Success: Created {len(chunks)} text chunks.")
    return chunks

def get_gemini_embedding(text):
    """Calls Google AI Studio to turn text into a multi-dimensional spatial coordinate array."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        # Extract the continuous block of coordinate values from Gemini's JSON response
        return np.array(response.json()["embedding"]["values"])
    else:
        raise Exception(f"Gemini API Error: {response.status_code} - {response.text}")

def semantic_search(query, document_chunks, chunk_embeddings, top_k=2):
    """Calculates spatial dot products to instantly extract the most relevant segments."""
    print(f"🔍 Vectorizing query: '{query}'")
    query_embedding = get_gemini_embedding(query)
    
    scores = []
    for idx, chunk_emb in enumerate(chunk_embeddings):
        # The exact same math you ran in your matrix_test.py script
        similarity = np.dot(query_embedding, chunk_emb)
        scores.append((similarity, document_chunks[idx]))
        
    # Sort the chunks by highest similarity score first
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]

# --- Integration Execution Block ---
if __name__ == "__main__":
    print("--- Local RAG Engine Active ---")
    
    # 1. Provide a quick testing string block or point it toward a document
    sample_text = "Our high-ticket automation factory code asset uses grok_spy_team.py to scan market triggers. The data_scraper.py tool safely pulls network code arrays directly from target servers."
    
    # Simulate a chunk database
    chunks = [
        "Our high-ticket automation factory code asset uses grok_spy_team.py to scan market triggers.",
        "The data_scraper.py tool safely pulls network code arrays directly from target servers.",
        "Calculus and algebra are standard foundations for building neural weights and backpropagation engines."
    ]
    
    if GEMINI_API_KEY == "YOUR_FALLBACK_API_KEY_HERE":
        print("⚠️ Please set your GEMINI_API_KEY inside the script or environment variables to pull live vectors.")
    else:
        print("🔗 Sourcing spatial coordinates from cloud architecture...")
        try:
            # Generate a coordinate array matrix for each chunk
            embeddings = [get_gemini_embedding(c) for c in chunks]
            
            # Execute a mathematical test search
            user_query = "how do I harvest server data"
            results = semantic_search(user_query, chunks, embeddings)
            
            print("\n🎯 Top Mathematically Matching Segments Found:")
            for score, text in results:
                print(f"[{score:.4f}] -> {text}")
                
        except Exception as e:
            print(f"❌ Operation Failed: {e}")
