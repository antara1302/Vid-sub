from dotenv import load_dotenv

from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
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
        try:
            print("YouTube URL detected.")
            print("Trying to fetch YouTube transcript...")

            transcript = get_youtube_transcript(video_id)

            if not transcript:
                raise RuntimeError("YouTube transcript is empty.")

            print("✅ YouTube transcript found.")
            print(
                f"Raw transcript (first 300 characters): "
                f"{transcript[:300]}"
            )

        except Exception as e:
            print(
                f"⚠️ YouTube transcript unavailable: "
                f"{type(e).__name__}: {e}"
            )
            print("Falling back to audio transcription...")

            # Import only when fallback is actually needed.
            from utils.audio_processor import process_input

            chunks = process_input(source)

            transcript = transcribe_all(
                chunks,
                language
            )

    else:
        # Local file / non-YouTube input
        from utils.audio_processor import process_input

        chunks = process_input(source)

        transcript = transcribe_all(
            chunks,
            language
        )

    print(
        f"Raw transcription (first 300 characters): "
        f"{transcript[:300]}"
    )

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