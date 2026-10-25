import os
from urllib.parse import urlparse, parse_qs

from google import genai


def extract_video_id(source: str) -> str | None:
    """Extract a YouTube video ID from common URL formats."""
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


def get_youtube_transcript(
    video_id: str,
    languages: list[str] | None = None,
) -> str:
    """
    Generate a transcript using Gemini's YouTube video input.
    The video must be public and accessible to Gemini.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY or GEMINI_API_KEY."
        )

    client = genai.Client(api_key=api_key)

    video_url = (
        f"https://www.youtube.com/watch?v={video_id}"
    )

    language_instruction = ""
    if languages:
        language_instruction = (
            f"Transcribe in the following preferred language(s): "
            f"{', '.join(languages)}. "
            "If the requested language is not spoken, "
            "preserve the original spoken language."
        )

    prompt = f"""
    Create a faithful, detailed transcript of all audible speech
    in this video.

    Requirements:
    - Preserve the spoken words and their original order.
    - Add readable punctuation and paragraph breaks.
    - Do not summarize, paraphrase, or invent dialogue.
    - Do not describe visuals or add commentary.
    - If a section is unintelligible, mark it as [unclear].
    {language_instruction}

    Return the transcript only.
    """

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=[
            {"type": "text", "text": prompt},
            {"type": "video", "uri": video_url},
        ],
    )

    transcript = (response.output_text or "").strip()

    if not transcript:
        raise RuntimeError(
            "Gemini returned an empty transcript."
        )

    return transcript




# from urllib.parse import urlparse, parse_qs

# from youtube_transcript_api import YouTubeTranscriptApi


# def extract_video_id(source: str) -> str | None:
#     """
#     Extract a YouTube video ID from common YouTube URL formats.
#     """

#     try:
#         parsed = urlparse(source)

#         # https://youtu.be/VIDEO_ID
#         if parsed.hostname in ["youtu.be", "www.youtu.be"]:
#             return parsed.path.lstrip("/").split("/")[0]

#         # https://www.youtube.com/watch?v=VIDEO_ID
#         if parsed.hostname in [
#             "youtube.com",
#             "www.youtube.com",
#             "m.youtube.com",
#         ]:
#             if parsed.path == "/watch":
#                 return parse_qs(parsed.query).get("v", [None])[0]

#             # https://www.youtube.com/shorts/VIDEO_ID
#             if parsed.path.startswith("/shorts/"):
#                 return parsed.path.split("/")[2]

#             # https://www.youtube.com/embed/VIDEO_ID
#             if parsed.path.startswith("/embed/"):
#                 return parsed.path.split("/")[2]

#     except Exception:
#         pass

#     return None


# def get_youtube_transcript(
#     video_id: str,
#     languages: list[str] | None = None
# ) -> str:
#     """
#     Fetch a YouTube transcript in the requested language(s)
#     and return plain text.
#     """

#     if languages is None:
#         languages = ["en"]

#     api = YouTubeTranscriptApi()

#     transcript = api.fetch(
#         video_id,
#         languages=languages,
#     )

#     return " ".join(
#         snippet.text
#         for snippet in transcript
#     ).strip()