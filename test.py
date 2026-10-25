from dotenv import load_dotenv
from core.youtube_transcript import (
    extract_video_id,
    get_youtube_video_notes,
)

load_dotenv()

url = "https://www.youtube.com/watch?v=F03rgsiXjac"

video_id = extract_video_id(url)
print("Video ID:", video_id)

if not video_id:
    raise ValueError("Invalid YouTube URL")

notes = get_youtube_video_notes(video_id, languages=["en"])

print("\n===== GENERATED VIDEO NOTES =====\n")
print(notes)