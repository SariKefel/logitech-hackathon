from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import ollama
import os

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("docs")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"status": "Local AI Assistant Backend Running", "privacy": "100% Local"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a text file"""
    try:
        content = await file.read()
        text = content.decode("utf-8")

        # Simple chunking: split by double newlines (paragraphs)
        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

        # If no double newlines, split by single newlines
        if len(chunks) <= 1:
            chunks = [chunk.strip() for chunk in text.split("\n") if chunk.strip()]

        # Generate embeddings and store in ChromaDB
        for i, chunk in enumerate(chunks):
            if len(chunk) > 10:  # Only process meaningful chunks
                embedding_response = ollama.embeddings(
                    model="llama3.2:3b",
                    prompt=chunk
                )
                collection.add(
                    ids=[f"{file.filename}_{i}"],
                    embeddings=[embedding_response["embedding"]],
                    documents=[chunk],
                    metadatas=[{"filename": file.filename, "chunk_id": i}]
                )

        return {
            "status": "success",
            "filename": file.filename,
            "chunks_processed": len(chunks)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with RAG support"""
    try:
        query = request.message

        # Get embedding for the query
        query_embedding = ollama.embeddings(
            model="llama3.2:3b",
            prompt=query
        )

        # Search ChromaDB for relevant context
        results = collection.query(
            query_embeddings=[query_embedding["embedding"]],
            n_results=3
        )

        # Build context from retrieved documents
        context = ""
        if results["documents"] and len(results["documents"][0]) > 0:
            context = "\n\n".join(results["documents"][0])

        # Create prompt with context
        if context:
            system_prompt = f"""You are a helpful local AI assistant. You have access to the following context from the user's documents:

{context}

Use this context to answer the user's question. If the answer isn't in the context, say so and provide a general helpful response."""
        else:
            system_prompt = "You are a helpful local AI assistant running entirely on the user's device. Be concise and helpful."

        # Generate response using Ollama
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )

        return {
            "response": response["message"]["content"],
            "context_used": bool(context)
        }
    except Exception as e:
        return {"response": f"Error: {str(e)}", "context_used": False}

@app.get("/health")
async def health_check():
    """Check if Ollama and ChromaDB are working"""
    try:
        # Test Ollama
        ollama.list()
        ollama_status = "connected"
    except:
        ollama_status = "disconnected"

    try:
        # Test ChromaDB
        collection.count()
        chromadb_status = "connected"
        doc_count = collection.count()
    except:
        chromadb_status = "disconnected"
        doc_count = 0

    return {
        "ollama": ollama_status,
        "chromadb": chromadb_status,
        "documents_stored": doc_count
    }
