import nemo.collections.asr as nemo_asr


class NemoASR:
    def __init__(self) -> None:
        self.asr_model = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(
            model_name="stt_hi_conformer_ctc_medium"
        )

    def transcribe_audio(self, audio_file):
        return self.asr_model.transcribe(paths2audio_files=[audio_file], batch_size=1)
