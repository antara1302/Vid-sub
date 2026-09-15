import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
    )


def extract_meeting_data(transcript: str) -> dict:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting analyst.

Analyze the meeting transcript and extract:

1. Action items:
   - task
   - owner
   - deadline

2. Key decisions:
   - decision

3. Open questions:
   - unresolved question or topic needing follow-up

Return ONLY valid JSON in exactly this format:

{{
    "action_items": [
        {{
            "task": "...",
            "owner": "...",
            "deadline": "..."
        }}
    ],
    "key_decisions": [
        {{
            "decision": "..."
        }}
    ],
    "open_questions": [
        {{
            "question": "..."
        }}
    ]
}}

Rules:
- Do not invent information.
- If an owner is not mentioned, use "Not specified".
- If a deadline is not mentioned, use "Not specified".
- If there are no items in a category, return an empty list.
- Return ONLY JSON. No markdown or explanation.
""",
        ),
        ("human", "{transcript}"),
    ])

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "transcript": transcript
    })

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("Warning: Gemini returned invalid JSON.")
        return {
            "action_items": [],
            "key_decisions": [],
            "open_questions": [],
        }