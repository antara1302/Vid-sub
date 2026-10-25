import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from core.transcriber import transcribe_all
from core.local_video import extract_audio_chunks
from core.summarizer import summarize, generate_title
from core.rag_engine import build_rag_chain
from core.youtube_transcript import (
    extract_video_id,
    get_youtube_video_notes,
)

load_dotenv()


def run_pipeline(
    source: str,
    language: str = "english",
    uploaded_video=None,
) -> dict:
    print("Starting AI Video Assistant")

    temp_video_path = None
    chunk_paths = []

    try:
        video_id = extract_video_id(source) if source else None

        if video_id and uploaded_video is not None:
            raise ValueError(
                "Please enter a YouTube URL or upload a local video, not both."
            )

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

        elif uploaded_video is not None:
            print("Local video uploaded. Extracting audio...")

            suffix = Path(uploaded_video.name).suffix or ".mp4"

            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temp_video:
                temp_video.write(uploaded_video.getbuffer())
                temp_video_path = temp_video.name

            chunk_paths = extract_audio_chunks(temp_video_path)

            print(f"Created {len(chunk_paths)} audio chunks.")
            content = transcribe_all(
                chunk_paths,
                language=language,
            )
            content_type = "transcript"

        else:
            raise ValueError(
                "Enter a valid YouTube URL or upload a local video."
            )

        if not content or not content.strip():
            raise RuntimeError("No usable notes or transcript were generated.")

        summary = summarize(content)
        title = generate_title(summary)

        if content_type == "transcript":
            # Preserve the meeting extraction flow for local transcriptions.
            from core.extractor import extract_meeting_data
            meeting_data = extract_meeting_data(content)
        else:
            meeting_data = {
                "action_items": [],
                "key_decisions": [],
                "open_questions": [],
            }

        rag_chain = build_rag_chain(content)

        return {
            "title": title,
            "transcript": content,
            "summary": summary,
            "action_items": meeting_data["action_items"],
            "key_decisions": meeting_data["key_decisions"],
            "open_questions": meeting_data["open_questions"],
            "rag_chain": rag_chain,
            "content_type": content_type,
        }

    finally:
        # Remove the uploaded video and its extracted audio chunks.
        temp_dirs = {
            str(Path(path).parent)
            for path in chunk_paths
        }

        for temp_dir in temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)

        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)


if __name__ == "__main__":
    source = input("Enter a public YouTube URL: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"

    result = run_pipeline(source, language)

    print(f"\nTitle: {result['title']}")
    print(f"\nContent:\n{result['transcript']}")
    print(f"\nSummary:\n{result['summary']}")
