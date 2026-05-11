import json
import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


SYSTEM_PROMPT = """
You are an expert hiring assistant.

Extract structured hiring requirements
from recruiter conversations.

Return ONLY valid JSON.

Fields:
- role
- seniority
- skills
- experience
- assessment_goal

If information is missing:
- use "" for strings
- use [] for arrays

Example:

{
  "role": "financial analyst",
  "seniority": "graduate",
  "skills": [
    "financial analysis",
    "situational judgement"
  ],
  "experience": "0 years",
  "assessment_goal": "hiring"
}
"""


def extract_state(messages):

    conversation = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in messages
    ])

    prompt = f"""
Extract structured hiring requirements
from this conversation.

Conversation:
{conversation}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = (
        response.choices[0]
        .message.content
        .strip()
    )

    # ----------------------------------------
    # SAFE JSON PARSING
    # ----------------------------------------

    try:

        # remove markdown if GPT returns ```json
        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(content)

        return {
            "role": parsed.get("role", ""),
            "seniority": parsed.get("seniority", ""),
            "skills": parsed.get("skills", []),
            "experience": parsed.get("experience", ""),
            "assessment_goal": parsed.get("assessment_goal", "")
        }

    except Exception:

        return {
            "role": "",
            "seniority": "",
            "skills": [],
            "experience": "",
            "assessment_goal": ""
        }