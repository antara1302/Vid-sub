import os
import subprocess
import tempfile
from pathlib import Path
from pydub import AudioSegment


def extract_audio_chunks(video_path: str, chunk_seconds: int = 25) -> list[str]:
    """Extract audio from a video and return paths to WAV chunks."""
    temp_dir = tempfile.mkdtemp(prefix="vidsub_")
    audio_path = os.path.join(temp_dir, "audio.wav")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vn",
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                audio_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        audio = AudioSegment.from_wav(audio_path)
        chunk_ms = chunk_seconds * 1000
        chunk_paths = []

        for index, start in enumerate(range(0, len(audio), chunk_ms)):
            chunk_path = os.path.join(temp_dir, f"chunk_{index}.wav")
            audio[start:start + chunk_ms].export(chunk_path, format="wav")
            chunk_paths.append(chunk_path)

        if not chunk_paths:
            raise RuntimeError("No audio was found in this video.")

        return chunk_paths

    except Exception:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
