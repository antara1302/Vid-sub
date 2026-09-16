import os
import sys

from setup_env import setup, GENERATE_ONCE_JS,BGUTIL_SERVER_DIR

setup()
print("BGUTIL SERVER:", BGUTIL_SERVER_DIR)
print("GENERATE ONCE:", GENERATE_ONCE_JS)
print("SERVER EXISTS:", os.path.isdir(BGUTIL_SERVER_DIR))
print("SCRIPT EXISTS:", os.path.isfile(GENERATE_ONCE_JS))

import yt_dlp
from pydub import AudioSegment



# Load bgutil yt-dlp plugin
PLUGIN_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "bgutil-ytdlp-pot-provider",
        "plugin",
    )
)

if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

#folder to save all vdos:
DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)


#route to download youtube audio
def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s") #saves the audio in a particular format
    ydl_opts = {
        "format": "bestaudio/best",

        "js_runtimes": {
            "node": {},
            "quickjs": {},
        },
        "plugin_dirs": [PLUGIN_DIR],
        "extractor_args": {
            "youtubepot-bgutilscript": {
                "server_home": "bgutil-ytdlp-pot-provider/server"
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },

        "outtmpl": output_path,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        "quiet": False,
        "verbose": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename

#data = download_youtube_audio("https://youtu.be/sg0EKLJgjMc?si=G-KSwXXrrCy8AzUE")

#mono-audio 16 KHz
def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

#final_data = convert_to_wav(data)

#chunking the audio(if the audio is too long)
def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

#print(chunk_audio(final_data))


#function to make this conversion process inputable
def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks

