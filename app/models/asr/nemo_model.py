import nemo.collections.asr as nemo_asr
from .asr import ASR
from typing import Union
import numpy as np
import torch


@ASR.register("nemo")
class NemoASR(ASR):
    """
    Transcribe audio using NeMo ASR model

    Attributes
    ----------
    model_name: ``str``
        The name of the model to use. The options are "stt_hi_conformer_ctc_medium" and "stt_hi_conformer_ctc_large"
    device: ``str``
        The device to run the model on. The options are "cpu" and "cuda"
    """

    def __init__(
        self, model_name: str = "stt_hi_conformer_ctc_medium", device: str = "cpu"
    ) -> None:
        self.device = device
        self.asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(
            model_name=model_name,
        ).to(device)

    def transcribe_audio(self, audio: Union[torch.Tensor, np.ndarray]):
        pass

    def transcribe_audio_file(self, audio_file: str):
        """
        Transcribe the audio file at the given path using the NeMo ASR model

        Parameters
        ----------
        audio_file: ``str``
            The path to the audio file to transcribe

        Returns
        -------
        ``str``
            The transcription of the audio file
        """
        return self.asr_model.transcribe(
            paths2audio_files=[audio_file], batch_size=1, verbose=False
        )
