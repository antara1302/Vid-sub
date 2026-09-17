from youtube_transcript_api import YouTubeTranscriptApi

video_id = "PeMlggyqz0Y"

try:
    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=["en"]
    )

    print("\n✅ TRANSCRIPT FOUND!\n")

    for snippet in transcript:
        print(snippet.text)

except Exception as e:
    print("\n❌ TRANSCRIPT FAILED")
    print(type(e).__name__)
    print(e)