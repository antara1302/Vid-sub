import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )


def summarize(transcript: str) -> str:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting summarizer.

Summarize the following meeting transcript.

Focus on:
- Main topics discussed
- Important points
- Key decisions
- Important conclusions

Keep the summary concise and professional.
Use clear bullet points.

Do not invent information that is not present in the transcript.
""",
        ),
        ("human", "{transcript}"),
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "transcript": transcript
    })


def generate_title(summary: str) -> str:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """Generate a short professional title for this meeting summary.

Maximum 8 words.
Return ONLY the title.
Do not use quotation marks.
""",
        ),
        ("human", "{summary}"),
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "summary": summary
    })