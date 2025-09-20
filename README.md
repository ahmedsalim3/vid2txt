# vid2txt

A Python package for transcribing videos/audios to text using various speech-to-text services. Currently supports AssemblyAI for high-quality transcription.

## Features

- Download and transcribe from YouTube or any URL (via `yt-dlp`)
- Extract audio from video files using `FFmpeg`
- Direct support for audio formats (MP3, WAV, M4A, AAC, FLAC, OGG, WMA)
- Transcribe audio using AssemblyAI API
- Export transcripts in multiple formats:
    - Plain text (.txt)
    - SubRip subtitles (.srt)
    - Interactive HTML (.html) with embedded video/audio player
- Language forcing support

## Installation

Install from source:

```bash
git clone https://github.com/ahmedsalim3/vid2txt.git
cd vid2txt
pip install -e .
```

## Setup

Set your AssemblyAI API key as an environment variable:

```bash
export ASSEMBLYAI_API_KEY="your-api-key-here"

# On Windows (PowerShell):
$env:ASSEMBLYAI_API_KEY="your-api-key-here"
```

Get a free API key from: [https://www.assemblyai.com/dashboard/signup](https://www.assemblyai.com/dashboard/signup)

## Usage

### Command Line Interface

```bash
vid2txt MEDIA_PATH [OPTIONS]
```

Where `MEDIA_PATH` can be:
- A local video file (.mp4, .mkv, .mov, ...)
- A local audio file (.mp3, .wav, ...)
- A YouTube or other URL

#### Options

- `-o, --output-dir`: Output directory (default: same as input file)
- `-l, --language`: Force transcription language (e.g., 'en', 'ar', 'es')
- `--model`: Speech-to-text model to use (currently only 'assemblyai')
- `--force-audio-extract`: Force re-extraction of audio from video files
- `--audio`: Download audio only when using YouTube URLs (faster)

#### Examples

```bash
# Transcribe a local video file
vid2txt video.mp4

# Transcribe a local audio file
vid2txt podcast.mp3

# Transcribe from YouTube (downloads best video+audio)
vid2txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download and transcribe audio only (faster)
vid2txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --audio

# Specify output directory and language
vid2txt https://www.youtube.com/watch?v=dQw4w9WgXcQ -o ./output -l en

# Force re-extraction of audio even if cached
vid2txt video.mp4 --force-audio-extract

# Show help
vid2txt -h
```

### Python API

```python
from vid2txt import Transcriber
from pathlib import Path

media_path = Path("video.mp4") # or Path("audio.mp3"), or a URL
output_dir = Path("output") # Output directory
api_key = "your_api_key" # if using assemblyai


transcriber = Transcriber(
    output_dir=output_dir,
    language="en",
    model="assemblyai",
    api_key=api_key
)


segments = transcriber.transcribe(media_path=media_path)

# Save in different formats
transcriber.save_plain_text(
    segments=segments, 
    out_path=output_dir / Path("transcript.txt")
)
transcriber.save_srt(
    segments=segments,
    out_path=output_dir / Path("transcript.srt")
)
transcriber.save_html(
    segments=segments, 
    out_path=output_dir / Path("transcript.html"), 
    media_path=media_path
)
```

# Contributing

Contributions are welcome, feel free to open an issue or submit a pull request

Here are a few ideas for future development:

### TODO

- Add support for additional speech-to-text models (e.g., OpenAI Whisper or other open-source models)
- Extend the [Summarizer](./vid2txt/utils/summarizer.py) to generate concise summaries of transcripts
- Extend the [Translator](./vid2txt/utils/translator.py) to support source → target language translation
