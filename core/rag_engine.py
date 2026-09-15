import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever,
)


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )


def format_docs(docs):
    return "\n\n".join(
        doc.page_content for doc in docs
    )


def build_rag_chain(transcript: str):

    # 1. Build vector store from transcript
    vector_store = build_vector_store(transcript)

    # 2. Create retriever
    retriever = get_retriever(vector_store, k=4)

    # 3. Create Gemini LLM
    llm = get_llm()

    # 4. Prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant.

            Answer the user's question based ONLY on the meeting transcript
            context provided below.

            If the answer is not found in the context, say:
            "I could not find this information in the meeting transcript."

            Always be concise and precise.
            If quoting someone, mention it clearly.

            Context from meeting transcript:
            {context}
            """,
        ),
        ("human", "{question}"),
    ])

    # 5. LCEL RAG pipeline
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():

    # 1. Load existing vector store
    vector_store = load_vector_store()

    # 2. Create retriever
    retriever = get_retriever(vector_store, k=4)

    # 3. Create Gemini LLM
    llm = get_llm()

    # 4. Prompt
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant.

            Answer the user's question based ONLY on the meeting transcript
            context provided below.

            If the answer is not found in the context, say:
            "I could not find this information in the meeting transcript."

            Always be concise and precise.
            If quoting someone, mention it clearly.

            Context from meeting transcript:
            {context}
            """,
        ),
        ("human", "{question}"),
    ])

    # 5. LCEL RAG pipeline
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str) -> str:

    print(f"Question: {question}")

    answer = rag_chain.invoke(question)

    print(f"Answer: {answer}")

    return answer