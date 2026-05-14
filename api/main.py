from fastapi import FastAPI

from pydantic import BaseModel

from typing import List

from rag.chatbot import chat


app = FastAPI()


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

@app.api_route("/health", methods=["GET", "HEAD"])
def health():

    return {
        "status": "ok"
    }