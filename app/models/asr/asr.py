from registrable import Registrable
import numpy as np
import torch
from typing import Union
from abc import abstractmethod


class ASR(Registrable):
    def __init__(self, model_name: str, device: str):
        self.model_name = model_name
        self.device = device

    @abstractmethod
    def transcribe_audio(self, audio: Union[torch.Tensor, np.ndarray]) -> str:
        raise NotImplementedError("transcribe_audio method not implemented")

    @abstractmethod
    def transcribe_audio_file(self, audio_file: str) -> str:
        raise NotImplementedError("transcribe_audio_file method not implemented")
