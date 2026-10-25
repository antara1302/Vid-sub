from pathlib import Path
from dotenv import load_dotenv

from core.transcriber import transcribe_all
from core.summarizer import (
    summarize,
    generate_title,
    translate_to_english,
)
from core.extractor import extract_meeting_data
from core.rag_engine import build_rag_chain
from core.youtube_transcript import (
    extract_video_id,
    get_youtube_video_notes,
)

load_dotenv()


def run_pipeline(source: str, language: str = "english") -> dict:
    print("Starting AI Video Assistant")

    video_id = extract_video_id(source)

    if video_id:
        print("YouTube URL detected. Generating video notes...")

        languages = (
            ["hi", "en"]
            if language.lower() == "hinglish"
            else ["en"]
        )

        content = get_youtube_video_notes(
            video_id,
            languages=languages,
        )
        content_type = "video_notes"

    else:
        file_path = Path(source).expanduser()

        if not file_path.is_file():
            raise ValueError(
                "Please provide a valid YouTube URL or existing local file."
            )

        raise NotImplementedError(
            "Local-file transcription is unchanged but needs the existing "
            "audio extraction/chunking pipeline to be connected here."
        )

    if not content or not content.strip():
        raise RuntimeError("No usable video notes were generated.")

    # The YouTube content is already structured notes.
    # Do not translate it as if it were a raw transcript.
    summary = summarize(content)
    title = generate_title(summary)

    # The meeting extractor expects a meeting transcript.
    # Don't invent meeting actions from ordinary video notes.
    meeting_data = {
        "action_items": [],
        "key_decisions": [],
        "open_questions": [],
    }

    rag_chain = build_rag_chain(content)

    return {
        "title": title,
        "transcript": content,  # Kept for app.py compatibility
        "summary": summary,
        "action_items": meeting_data["action_items"],
        "key_decisions": meeting_data["key_decisions"],
        "open_questions": meeting_data["open_questions"],
        "rag_chain": rag_chain,
        "content_type": content_type,
    }


if __name__ == "__main__":
    source = input("Enter a public YouTube URL: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"

    result = run_pipeline(source, language)

    print(f"\nTitle: {result['title']}")
    print(f"\nVideo Notes:\n{result['transcript']}")
    print(f"\nSummary:\n{result['summary']}")

    print("\nChat with the video notes (type 'exit' to quit).")
    rag_chain = result["rag_chain"]

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit", "q"}:
            break
        if not question:
            continue

        print(f"\nAssistant: {rag_chain.invoke(question)}\n")
