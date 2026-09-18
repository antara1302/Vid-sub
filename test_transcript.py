from core.youtube_transcript import get_youtube_transcript


video_id = "PeMlggyqz0Y"

try:
    text = get_youtube_transcript(video_id)

    print("\n✅ Transcript extracted")
    print("\nFirst 1000 characters:\n")
    print(text[:1000])

except Exception as e:
    print("\n❌ Transcript extraction failed")
    print(type(e).__name__)
    print(e)