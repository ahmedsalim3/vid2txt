# some functions were
# inspired from https://github.com/pH-7/Download-Simply-Videos-From-YouTube/blob/main/download.py

from pathlib import Path
import os
from urllib.parse import urlparse, parse_qs
from functools import lru_cache

from yt_dlp import YoutubeDL
import ffmpeg


@lru_cache(maxsize=128)
def get_url_info(url: str) -> str:
    """Get content type of the provided URL (video, playlist, or channel)."""
    try:
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "no_warnings": True,
            "skip_download": True,
            "playlist_items": "1",
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                if "/@" in url or "/channel/" in url or "/c/" in url or "/user/" in url:
                    return "channel"
                elif "list" in query_params:
                    return "playlist"
                else:
                    return "video"

            content_type = info.get("_type", "video")
            if (
                content_type == "playlist"
                and info.get("uploader_id")
                and (
                    "/@" in url or "/channel/" in url or "/c/" in url or "/user/" in url
                )
            ):
                return "channel"
            return content_type

    except Exception:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if "/@" in url or "/channel/" in url or "/c/" in url or "/user/" in url:
            return "channel"
        elif "list" in query_params:
            return "playlist"
        else:
            return "video"


def download_single_video(
    url: str, output_path: str, thread_id: int = 0, audio_only: bool = False
) -> dict:
    """
    Download a single media item (video or audio) from a supported site.

    :param url: Media URL (YouTube, Vimeo, TikTok, etc.)
    :param output_path: Directory to save the file
    :param thread_id: Thread ID for logging (unused, kept for compatibility)
    :param audio_only: Whether to download audio only
    :return: Dictionary with success status and message
    """
    if audio_only:
        format_selector = "bestaudio/best"
        file_extension = "mp3"
        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    else:
        format_selector = "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
        file_extension = "mp4"
        postprocessors = [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ]

    ydl_opts = {
        "format": format_selector,
        "ignoreerrors": True,
        "no_warnings": True,
        "extract_flat": False,
        "writesubtitles": False,
        "writethumbnail": False,
        "writeautomaticsub": False,
        "postprocessors": postprocessors,
        "keepvideo": False,
        "clean_infojson": True,
        "retries": 3,
        "fragment_retries": 3,
        "noplaylist": True,
    }

    if not audio_only:
        ydl_opts["merge_output_format"] = "mp4"

    ydl_opts["outtmpl"] = os.path.join(output_path, f"%(title)s.{file_extension}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return {
                    "url": url,
                    "success": False,
                    "message": "Failed to extract media information",
                }

            if info.get("_type") == "playlist":
                return {
                    "url": url,
                    "success": False,
                    "message": "URL appears to be a playlist. Please provide a direct media URL.",
                }

            ydl.download([url])
            return {"url": url, "success": True, "message": "Download completed"}

    except Exception as e:
        return {"url": url, "success": False, "message": str(e)}


def is_url(path: str) -> bool:
    """Check if a string is a valid URL."""
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https", "ftp") and parsed.netloc != ""


def download_video(url: str, output_dir: str = "output") -> str:
    """
    Download a video (mp4) from a supported site and return the saved file path.

    :param url: Media URL (YouTube, Vimeo, TikTok, etc.)
    :param output_dir: Directory to save the file
    :return: Path to downloaded video
    """
    if not is_url(url):
        return url

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result = download_single_video(url, str(output_path), audio_only=False)
    if not result["success"]:
        raise Exception(f"Video download failed: {result['message']}")

    files = list(output_path.glob("*.mp4"))
    if not files:
        files = [
            f
            for f in output_path.glob("*.*")
            if f.suffix.lower() in [".mp4", ".mkv", ".avi", ".mov", ".webm"]
        ]
    if not files:
        raise Exception("Download completed but no video file found")

    return str(max(files, key=lambda x: x.stat().st_mtime))


def download_audio(url: str, output_dir: str = "output") -> str:
    """
    Download an audio track (mp3) from a supported site and return the saved file path.

    :param url: Media URL (YouTube, SoundCloud, TikTok, etc.)
    :param output_dir: Directory to save the file
    :return: Path to downloaded audio
    """
    if not is_url(url):
        return url

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result = download_single_video(url, str(output_path), audio_only=True)
    if not result["success"]:
        raise Exception(f"Audio download failed: {result['message']}")

    files = list(output_path.glob("*.mp3"))
    if not files:
        files = [
            f
            for f in output_path.glob("*.*")
            if f.suffix.lower() in [".mp3", ".m4a", ".aac", ".wav", ".flac"]
        ]
    if not files:
        raise Exception("Download completed but no audio file found")

    return str(max(files, key=lambda x: x.stat().st_mtime))


def extract_audio(video_path, output_dir=None, force=False):
    """
    Extract audio from a video file using ffmpeg.
    The audio is saved as a WAV file with the following properties:
    - PCM 16-bit encoding
    - Mono channel
    - 16 kHz sample rate
    """
    video_path = Path(video_path)
    if output_dir is None:
        output_audio = video_path.with_name(f"{video_path.stem}.audio.wav")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_audio = Path(output_dir) / f"{video_path.name}.audio.wav"

    if output_audio.exists() and not force:
        return output_audio

    stream = ffmpeg.input(str(video_path))
    stream = ffmpeg.output(
        stream,
        str(output_audio),
        ar=16000,
        ac=1,
        acodec="pcm_s16le",
    )

    ffmpeg.run(stream, overwrite_output=True, quiet=True)

    return output_audio


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print("Downloading video...")
    video_path = download_video(video_url, output_dir="downloads/videos")
    print(f"Video saved at: {video_path}")

    print("Extracting audio from video...")
    audio_path = extract_audio(video_path, output_dir="downloads/extracted_audios")
    print(f"Extracted audio saved at: {audio_path}")

    print("Downloading audio...")
    audio_path = download_audio(video_url, output_dir="downloads/audios")
    print(f"Audio saved at: {audio_path}")
