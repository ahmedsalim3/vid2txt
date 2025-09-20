from pathlib import Path
import argparse
import os
import sys

from vid2txt.transcribe import Transcriber
from vid2txt.utils import media


def parse_args():
    parser = argparse.ArgumentParser(
        description="Video-to-Text transcription tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        %(prog)s video.mp4
        %(prog)s "https://youtube.com/watch?v=VIDEO_ID" --audio
        %(prog)s video.mp4 -o ./output --language en
        """,
    )
    parser.add_argument(
        "media_path", type=str, help="Video/audio file path or YouTube URL"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: same as input file)",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default=None,
        help="Force transcription language (e.g., 'en', 'ar', 'es')",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="assemblyai",
        choices=["assemblyai"],
        help="Speech-to-text model to use",
    )
    parser.add_argument(
        "--force-audio-extract",
        action="store_true",
        help="Force re-extraction of audio from video files",
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Download audio only when using YouTube URLs (faster)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate API key early
    if args.model == "assemblyai":
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            print("Error: ASSEMBLYAI_API_KEY environment variable is required.")
            print("Please set your API key: export ASSEMBLYAI_API_KEY='your-api-key'")
            print("get a free one from:: https://www.assemblyai.com/dashboard/signup")
            sys.exit(1)

    # Handle URL downloads
    if media.is_url(args.media_path):
        if args.output_dir is None:
            args.output_dir = "output"

        try:
            if args.audio:
                media_path = Path(
                    media.download_audio(args.media_path, str(args.output_dir))
                )
            else:
                media_path = Path(
                    media.download_video(args.media_path, str(args.output_dir))
                )
        except Exception as e:
            print(f"Download failed: {e}")
            sys.exit(1)
        output_dir = Path(args.output_dir)
    else:
        media_path = Path(args.media_path)
        if not media_path.exists():
            print(f"File not found: {media_path}")
            sys.exit(1)
        output_dir = Path(args.output_dir) if args.output_dir else media_path.parent

    # Initialize transcriber
    try:
        transcriber = Transcriber(
            output_dir=output_dir,
            language=args.language,
            model=args.model,
            api_key=api_key,
        )
    except Exception as e:
        print(f"Error: Failed to initialize transcriber: {e}")
        sys.exit(1)

    try:
        transcript_segments = transcriber.transcribe(
            media_path, force_audio_extract=args.force_audio_extract
        )
    except KeyboardInterrupt:
        print("Transcription cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Transcription failed: {e}")
        sys.exit(2)

    # Save output files
    try:
        base_name = media_path.stem
        txt_path = output_dir / f"{base_name}.txt"
        srt_path = output_dir / f"{base_name}.srt"
        html_path = output_dir / f"{base_name}.html"

        transcriber.save_plain_text(transcript_segments, txt_path)
        transcriber.save_srt(transcript_segments, srt_path)
        transcriber.save_html(transcript_segments, html_path, media_path)

        print(f"Files saved:")
        print(f"  - Text: {txt_path}")
        print(f"  - SRT: {srt_path}")
        print(f"  - HTML: {html_path}")
        print(f"Output directory: {output_dir}")
    except Exception as e:
        print(f"Error: Failed to save output files - {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
