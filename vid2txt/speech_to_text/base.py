from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional


class SpeechToText(ABC):
    """Base class for speech-to-text models."""

    def __init__(self, **kwargs):
        """
        Initialize the speech-to-text model.

        :param kwargs: specific parameters
        """

        # Store any additional parameters that subclasses might need
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def transcribe(self, audio_path: Path, **kwargs) -> List[Dict]:
        """
        Transcribe audio file to text segments.

        :param audio_path: Path to audio file
        :param kwargs: specific parameters
        :return: List of transcript segments with start, end, and text
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model."""
        pass
