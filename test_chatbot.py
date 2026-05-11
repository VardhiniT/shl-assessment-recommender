from rag.chatbot import chat

messages = [
    {
        "role": "user",
        "content": "Hiring Java backend engineer"
    },
    {
        "role": "assistant",
        "content": "What seniority level?"
    },
    {
        "role": "user",
        "content": "Senior IC with AWS and Docker"
    }
]

response = chat(messages)

print(response)