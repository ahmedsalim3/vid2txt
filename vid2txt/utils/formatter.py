from typing import List, Dict
from pathlib import Path
from datetime import timedelta

import html
import shutil
from jinja2 import Template


def _format_timestamp(seconds: float) -> str:
    """
    Format timestamp to SRT format: HH:MM:SS,mmm
    :param seconds: Time in seconds
    :return: Formatted timestamp
    """
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600 + td.days * 24
    remainder = seconds - hours * 3600
    h = hours
    m = int(remainder // 60)
    s = int(remainder % 60)
    return f"{h:02d}:{m:02d}:{s:02d},{milliseconds:03d}"


def segments_to_srt(segments: List[Dict]) -> str:
    """
    Convert segments to SRT format
    :param segments: List of segments
    :return: SRT formatted string
    """
    lines = []
    for i, seg in enumerate(segments, start=1):
        start = _format_timestamp(seg["start"])
        end = _format_timestamp(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")  # blank line
    return "\n".join(lines)


def segments_to_plain(segments: List[Dict]) -> str:
    """
    Convert segments to plain text format
    :param segments: List of segments
    :return: Plain text formatted string
    """
    blocks = []
    for seg in segments:
        start = _format_timestamp(seg["start"]).replace(",", ".")
        blocks.append(f"[{start}] {seg['text'].strip()}")
    return "\n\n".join(blocks)


def segments_to_html(
    segments: List[Dict],
    media_path: Path,
    output_dir: Path = None,
    language: str = None,
) -> str:
    """
    Convert segments to HTML format
    :param segments: List of segments
    :param media_path: Path to video or audio file
    :param output_dir: Output directory
    :param language: Language code
    :return: HTML formatted string
    """
    tpl = Template(
        Path(__file__)
        .parent.joinpath("templates", "transcript_template.html")
        .read_text(encoding="utf-8")
    )

    # copy media file to output directory if specified, otherwise use relative path
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / media_path.name
        if not dest.exists():
            shutil.copy2(media_path, dest)
        media_url = dest.name

    # determine if it's audio or video
    audio_exts = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma"}
    is_audio = media_path.suffix.lower() in audio_exts

    # detect RTL languages
    rtl_langs = {"ar", "he", "fa", "ur", "yi", "ji"}
    is_rtl = language in rtl_langs if language else False

    # pre-format timestamps for display
    formatted_segments = []
    for seg in segments:
        formatted = seg.copy()
        formatted["formatted_start"] = _format_timestamp(seg["start"]).replace(",", ".")
        formatted_segments.append(formatted)

    return tpl.render(
        segments=formatted_segments,
        media_url=media_url,
        is_audio=is_audio,
        is_rtl=is_rtl,
        escape=html.escape,
    )
