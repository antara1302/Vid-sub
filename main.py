from dotenv import load_dotenv

from core.transcriber import transcribe_all
from core.summarizer import (
    summarize,
    generate_title,
    translate_to_english,
)
from core.extractor import extract_meeting_data
from core.rag_engine import build_rag_chain, ask_question
from core.youtube_transcript import (
    extract_video_id,
    get_youtube_transcript,
)
load_dotenv()

def run_pipeline(source: str, language: str = "english") -> dict:
    print("Starting AI Video Assistant")

    # 1. Try YouTube transcript first
    video_id = extract_video_id(source)

    if video_id:
        print("YouTube URL detected.")
        print("Trying to fetch YouTube transcript...")

        if language.lower() == "hinglish":
            # Hindi videos commonly have Hindi auto-generated captions
            transcript = get_youtube_transcript(
                video_id,
                languages=["hi", "en"]
            )
        else:
            transcript = get_youtube_transcript(
                video_id,
                languages=["en"]
            )

        if not transcript:
            raise RuntimeError(
                "No usable YouTube transcript was found for this video."
            )

        print("✅ YouTube transcript found.")
        print(
            f"Raw transcript (first 300 characters): "
            f"{transcript[:300]}"
        )

    else:
        raise ValueError(
            "Please provide a valid YouTube URL."
        )

    #2. Transcript obtained above
    raw_transcript = transcript

    # Translate Hinglish/Hindi transcript to English
    if language.lower() == "hinglish":
        print("Translating Hinglish transcript to English...")
        transcript = translate_to_english(raw_transcript)
        print("✅ Translation complete.")


    # 3. Generate summary
    summary = summarize(transcript)

    # 4. Generate title from summary
    title = generate_title(summary)

    # 5. Extract action items, decisions, and questions
    meeting_data = extract_meeting_data(transcript)

    # 6. Build RAG chain
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": meeting_data["action_items"],
        "key_decisions": meeting_data["key_decisions"],
        "open_questions": meeting_data["open_questions"],
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":

    # CLI entry point
    source = input(
        "Enter YouTube URL or local file path: "
    ).strip()

    language = input(
        "Language (english/hinglish): "
    ).strip() or "english"

    result = run_pipeline(source, language)

    print("\n" + "=" * 60)

    print(f"📌 Title: {result['title']}")

    print(
        f"\n📋 Summary:\n"
        f"{result['summary']}"
    )

    print(
        f"\n✅ Action Items:\n"
        f"{result['action_items']}"
    )

    print(
        f"\n🔑 Key Decisions:\n"
        f"{result['key_decisions']}"
    )

    print(
        f"\n❓ Open Questions:\n"
        f"{result['open_questions']}"
    )

    print("=" * 60)

    # Phase 2 — Chat with your meeting via RAG
    print(
        "\n💬 Chat with your meeting "
        "(type 'exit' to quit)\n"
    )

    rag_chain = result["rag_chain"]

    while True:

        question = input("You: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        if not question:
            continue

        answer = ask_question(
            rag_chain,
            question
        )

        print(
            f"\n🤖 Assistant: {answer}\n"
        )