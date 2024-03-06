import whisper
from .speech_language_detection import SpeechLanguageDetection
import torch
import numpy as np
from typing import Union
from pathlib import Path


@SpeechLanguageDetection.register("whisper")
class WhisperModel(SpeechLanguageDetection):
    """
    Detect the language of an audio file using the whisper model

    Attributes
    ----------
    model: ``str``
        The name of the model to use. The options are "small" and "large"
    device: ``str``
        The device to run the model on. The options are "cpu" and "cuda"
    """

    def __init__(self, model_name: str = "small", device: str = "cpu") -> None:
        self.device = device
        self.model = whisper.load_model(model_name,download_root="/data1/muni/models/whisper")

    def detect_language_from_signal(
        self, audio: Union[torch.Tensor, np.ndarray]
    ) -> str:
        """
        Detect the language of the audio signal using the whisper model

        Parameters
        ----------
        audio: ``Union[torch.Tensor, np.ndarray]``
            The audio signal to detect the language

        Returns
        -------
        ``str``
            The detected language of the audio signal
        """
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        return detected_language

    def detect_language_from_file(self, audio_path: str) -> str:
        """
        Detect the language of the audio file using the whisper model

        Parameters
        ----------
        audio_path: ``str``
            The path to the audio file to detect the language

        Returns
        -------
        ``str``
            The detected language of the audio file
        """
        if isinstance(audio_path, Path):
            audio_path = str(audio_path)
        audio= whisper.load_audio(audio_path)
        return self.detect_language_from_signal(audio)
