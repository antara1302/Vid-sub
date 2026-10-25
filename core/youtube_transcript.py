
import os
from urllib.parse import urlparse, parse_qs

from google import genai


def extract_video_id(source: str) -> str | None:
    """Extract a YouTube video ID from common YouTube URL formats."""
    try:
        parsed = urlparse(source.strip())
        host = (parsed.hostname or "").lower()

        if host in {"youtu.be", "www.youtu.be"}:
            return parsed.path.strip("/").split("/")[0] or None

        if host in {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
        }:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in {
                "shorts", "embed", "live"
            }:
                return parts[1]

    except (ValueError, AttributeError):
        return None

    return None


def get_youtube_video_notes(
    video_id: str,
    languages: list[str] | None = None,
) -> str:
    """Generate structured notes from a public YouTube video."""

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv(
        "GEMINI_API_KEY"
    )
    if not api_key:
        raise RuntimeError("Missing Gemini API key.")

    client = genai.Client(api_key=api_key)
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    language_instruction = ""
    if languages:
        language_instruction = (
            f"Prefer this language for the notes: "
            f"{', '.join(languages)}."
        )

    prompt = f"""
    Analyze this video and create useful, detailed notes.

    Include:
    - Main topic and purpose
    - Key concepts and explanations
    - Important examples
    - Key takeaways
    - Conclusion

    Use original wording. Do not provide a verbatim transcript
    or reproduce extended passages of dialogue.
    Do not invent details or claim these notes are complete.
    {language_instruction}

    Return well-structured Markdown.
    """

    response = client.interactions.create(
        model="gemini-2.5-flash",
        input=[
            {"type": "text", "text": prompt},
            {"type": "video", "uri": video_url},
        ],
    )

    notes = (response.output_text or "").strip()

    if not notes:
        raise RuntimeError("Gemini returned empty video notes.")

    return notes
