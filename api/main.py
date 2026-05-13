from contextlib import asynccontextmanager

from fastapi import FastAPI

from pydantic import BaseModel

from typing import List

from rag.chatbot import chat


# --------------------------------------------------
# WARMUP ON STARTUP
# pre-loads embedding model + ChromaDB before
# the first request arrives — prevents slow first call
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Warming up embedding model and vector DB...")

    try:

        from rag.embeddings import embedding_model
        from rag.vector_store import collection

        embedding_model.encode("warmup")
        collection.get(limit=1)

        print("Warmup complete.")

    except Exception as e:

        print(f"Warmup warning (non-fatal): {e}")

    yield


app = FastAPI(lifespan=lifespan)


# --------------------------------------------------
# REQUEST SCHEMA
# --------------------------------------------------

class Message(BaseModel):

    role: str
    content: str


class ChatRequest(BaseModel):

    messages: List[Message]


# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------

@app.post("/chat")
def chat_endpoint(request: ChatRequest):

    messages = [
        {
            "role": m.role,
            "content": m.content
        }
        for m in request.messages
    ]

    response = chat(messages)

    return response


# --------------------------------------------------
# HEALTH ENDPOINT
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }