from pathlib import Path
from typing import List, Dict, Optional, Union

from vid2txt.utils import media as media_utils
from vid2txt.utils import formatter as formatter_utils
from vid2txt.speech_to_text import SpeechToText, AssemblyAI


class Transcriber:
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        language: Optional[str] = None,
        model: Union[str, SpeechToText] = "assemblyai",
        api_key: Optional[str] = None,
    ):
        """
        Transcriber with support for multiple speech-to-text models.

        :param output_dir: Directory to save outputs (audio/text)
        :param language: Force transcription language
        :param model: Speech-to-text model to use ("assemblyai" or SpeechToText instance)
        :param api_key: API key for the speech-to-text service
        """
        self.output_dir = Path(output_dir) if output_dir else None
        self.language = language

        output_dir.mkdir(parents=True, exist_ok=True) if output_dir else None

        # Initialize the speech-to-text model
        if isinstance(model, str):
            if model.lower() == "assemblyai":
                self.speech_to_text = AssemblyAI(
                    language=self.language, api_key=api_key
                )
            else:
                raise ValueError(
                    f"Unknown model: {model}. Supported models: 'assemblyai'"
                )
        elif isinstance(model, SpeechToText):
            self.speech_to_text = model

    def transcribe(
        self, media_path: Path, force_audio_extract: bool = False
    ) -> List[Dict]:
        """
        Transcribe a video or audio file.

        :param media_path: Path to video or audio file
        :param force_audio_extract: Force audio extraction even if it exists (only for video files)
        :return: List of transcript segments
        """
        media_path = Path(media_path)

        # Check if the file is already an audio file
        audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma"}
        if media_path.suffix.lower() in audio_extensions:
            return self.speech_to_text.transcribe(media_path)
        else:
            audio_path = media_utils.extract_audio(
                media_path, force=force_audio_extract
            )
            return self.speech_to_text.transcribe(audio_path)

    def get_model_name(self) -> str:
        """Get the name of the current speech-to-text model."""
        return self.speech_to_text.get_model_name()

    def save_plain_text(self, segments: List[Dict], out_path: Path):
        out_path.write_text(
            formatter_utils.segments_to_plain(segments), encoding="utf-8"
        )

    def save_srt(self, segments: List[Dict], out_path: Path):
        out_path.write_text(formatter_utils.segments_to_srt(segments), encoding="utf-8")

    def save_html(self, segments: List[Dict], out_path: Path, media_path: Path):
        html = formatter_utils.segments_to_html(
            segments, media_path, self.output_dir, self.language
        )
        out_path.write_text(html, encoding="utf-8")
