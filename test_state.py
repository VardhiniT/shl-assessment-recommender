from rag.state_extractor import extract_state


messages = [
    {
        "role": "user",
        "content": (
            "Hiring senior backend Java engineer "
            "with AWS and Docker"
        )
    }
]


state = extract_state(messages)

print(state)