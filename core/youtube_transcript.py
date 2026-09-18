from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(source: str) -> str | None:
    """
    Extract a YouTube video ID from common YouTube URL formats.
    """

    try:
        parsed = urlparse(source)

        # https://youtu.be/VIDEO_ID
        if parsed.hostname in ["youtu.be", "www.youtu.be"]:
            return parsed.path.lstrip("/").split("/")[0]

        # https://www.youtube.com/watch?v=VIDEO_ID
        if parsed.hostname in [
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
        ]:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            # https://www.youtube.com/shorts/VIDEO_ID
            if parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[2]

            # https://www.youtube.com/embed/VIDEO_ID
            if parsed.path.startswith("/embed/"):
                return parsed.path.split("/")[2]

    except Exception:
        pass

    return None


def get_youtube_transcript(
    video_id: str,
    languages: list[str] | None = None
) -> str:
    """
    Fetch a YouTube transcript in the requested language(s)
    and return plain text.
    """

    if languages is None:
        languages = ["en"]

    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=languages,
    )

    return " ".join(
        snippet.text
        for snippet in transcript
    ).strip()