from pathlib import Path
from typing import List, Dict, Optional
import time
import requests

from vid2txt.speech_to_text.base import SpeechToText


class AssemblyAI(SpeechToText):
    """AssemblyAI speech-to-text implementation."""

    def __init__(
        self, language: Optional[str] = None, api_key: Optional[str] = None, **kwargs
    ):
        """
        AssemblyAI speech-to-text implementation
        :param language: Language code for transcription
        :param api_key: AssemblyAI API key
        :param kwargs: Additional parameters
        """
        super().__init__(language=language, api_key=api_key, **kwargs)
        if not self.api_key:
            raise ValueError("AssemblyAI API key is required")

        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {"authorization": self.api_key}

    def transcribe(self, audio_path: Path) -> List[Dict]:
        def read_file(path: Path, chunk_size: int = 5_242_880):
            """
            Read file in chunks
            :param path: Path to file
            :param chunk_size: Size of each chunk
            :return: Generator of chunks
            """
            with open(path, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield chunk

        # upload audio
        upload_res = requests.post(
            f"{self.base_url}/upload", headers=self.headers, data=read_file(audio_path)
        )
        upload_res.raise_for_status()
        audio_url = upload_res.json()["upload_url"]

        # request transcription
        transcript_config = self._transcript_config(audio_url)
        trans_res = requests.post(
            f"{self.base_url}/transcript", headers=self.headers, json=transcript_config
        )
        trans_res.raise_for_status()
        job_id = trans_res.json()["id"]

        return self._poll_transcription(job_id)

    def get_model_name(self) -> str:
        """Get the name of the model."""
        return "AssemblyAI"

    def _transcript_config(self, audio_url: str) -> dict:
        """
        Transcript configuration
        :param audio_url: URL of the audio file
        :return: Transcript configuration
        """
        config = {"audio_url": audio_url, "speaker_labels": True}
        if self.language:
            config["language_code"] = self.language
        if not self.language or self.language in {"en", "en-US"}:
            config["word_boost"] = ["AssemblyAI", "transcription", "video", "audio"]
            config["boost_param"] = "high"
        return config

    def _poll_transcription(self, job_id: str) -> List[Dict]:
        """
        Poll AssemblyAI until transcription is complete
        :param job_id: ID of the transcription job
        :return: List of transcript segments
        """
        while True:
            poll_res = requests.get(
                f"{self.base_url}/transcript/{job_id}", headers=self.headers
            )
            poll_res.raise_for_status()
            data = poll_res.json()
            status = data["status"]

            if status == "completed":
                print(f"Status: {status}")
                return self._parse_transcript(job_id, data)

            if status == "error":
                raise RuntimeError(
                    f"AssemblyAI transcription failed: {data.get('error', 'Unknown error')}"
                )
            print(f"Status: {status}, waiting...")
            time.sleep(2)

    def _parse_transcript(self, job_id: str, transcript_data: dict) -> List[Dict]:
        """
        Convert transcript into time-coded segments
        :param job_id: ID of the transcription job
        :param transcript_data: Transcript data
        :return: List of transcript segments
        """
        words_data = transcript_data.get("words")
        if not words_data:
            try:
                words_res = requests.get(
                    f"{self.base_url}/transcript/{job_id}/words", headers=self.headers
                )
                if words_res.status_code == 200:
                    words_data = words_res.json().get("words")
            except Exception as e:
                print(f"Failed to fetch word-level timestamps: {e}")
                words_data = None

        if words_data:
            return self._create_segments_from_words(words_data)
        return self._create_segments_from_text(transcript_data.get("text", ""))

    def _create_segments_from_words(
        self, words: List[dict], segment_duration: float = 3.0
    ) -> List[Dict]:
        """
        Create segments based on word-level timestamps
        :param words: List of words
        :param segment_duration: Duration of each segment
        :return: List of transcript segments
        """
        segments, current = [], {"start": None, "end": None, "text": ""}
        for word in words:
            start, end = word["start"] / 1000.0, word["end"] / 1000.0
            if current["start"] is None:
                current["start"] = start
            current["end"] = end
            current["text"] += (" " if current["text"] else "") + word["text"]

            if (end - current["start"]) >= segment_duration or word == words[-1]:
                if current["text"].strip():
                    segments.append(current.copy())
                current = {"start": None, "end": None, "text": ""}
        return segments

    def _create_segments_from_text(self, text: str) -> List[Dict]:
        """
        Create segments based on plain text
        :param text: Transcript text
        :return: List of transcript segments
        """
        if not text:
            raise RuntimeError("No transcript text received from AssemblyAI")

        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if not sentences:
            return [{"start": 0.0, "end": 0.0, "text": text}]

        total_words = len(text.split())
        words_per_minute = 150

        segments, current_text, current_words, segment_start = [], "", 0, 0.0
        words_per_segment = max(8, total_words // len(sentences))

        for i, sentence in enumerate(sentences):
            current_text += sentence + ". "
            current_words += len(sentence.split())
            if current_words >= words_per_segment or i == len(sentences) - 1:
                segment_end = segment_start + (current_words / words_per_minute) * 60
                segments.append(
                    {
                        "start": segment_start,
                        "end": segment_end,
                        "text": current_text.strip(),
                    }
                )
                segment_start = segment_end
                current_text, current_words = "", 0
        return segments
