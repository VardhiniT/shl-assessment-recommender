import threading
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from rag.chatbot import chat

app = FastAPI()

# --------------------------------------------------
# BACKGROUND WARMUP
# Runs AFTER server is up and port is bound
# Does not block startup
# --------------------------------------------------

def warmup():
    try:
        from rag.embeddings import embedding_model
        from rag.vector_store import collection
        embedding_model.encode("warmup")
        collection.get(limit=1)
        print("Warmup complete.")
    except Exception as e:
        print(f"Warmup error (non-fatal): {e}")

threading.Thread(target=warmup, daemon=True).start()


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    messages = [
        {"role": m.role, "content": m.content}
        for m in request.messages
    ]
    return chat(messages)

@app.get("/health")
def health():
    return {"status": "ok"}