# Local AI Chatbot - Logitech Hackathon

## Quick Start (After Ollama is installed)

### 1. Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

### 3. Open Browser
Navigate to: http://localhost:3000

### 4. Test the Demo
1. Upload a `.txt` file
2. Ask questions about the document
3. Show off privacy & speed!

## Demo Script

1. **Privacy**: "Everything runs locally—no cloud, no APIs"
2. **Upload**: Demo file upload with meeting notes or any text
3. **Chat**: Ask "What are the main points?" or "Summarize this"
4. **Speed**: Point out instant responses (no network delay)
5. **Offline**: Disconnect Wi-Fi to show it still works

## Troubleshooting

- **"Ollama not found"**: Install from https://ollama.ai
- **"Connection refused"**: Make sure `ollama serve` is running
- **"Model not found"**: Run `ollama pull llama3.2:3b`
- **Backend not starting**: Check backend/chroma_db directory permissions

## Configuration

### Backend (`backend/main.py`)

**CORS Origins** (line 13)
```python
allow_origins=["http://localhost:3000"]
```
Change this if your frontend runs on a different port or domain.

**ChromaDB Storage Path** (line 20)
```python
client = chromadb.PersistentClient(path="./chroma_db")
```
Change this to store your vector database in a different location.

**Ollama Model** (lines 48, 74, 101)
```python
model="llama3.2:3b"
```
Change this to use a different Ollama model (e.g., `llama3.2:1b` for faster/lighter or `llama3.2:7b` for better quality).

**Collection Name** (line 21)
```python
collection = client.get_or_create_collection("docs")
```
Change this to use a different collection name for organizing documents.

### Frontend (`frontend/app/page.tsx`)

**Backend API URL** (lines 39, 64)
```typescript
fetch('http://localhost:8000/chat', ...)
fetch('http://localhost:8000/upload', ...)
```
Change `http://localhost:8000` if your backend runs on a different host or port.

## Architecture

- **Frontend**: Next.js 14 + React + Tailwind CSS
- **Backend**: FastAPI (Python)
- **LLM**: Ollama (llama3.2:3b)
- **Vector DB**: ChromaDB
- **RAG**: Embeddings + similarity search
