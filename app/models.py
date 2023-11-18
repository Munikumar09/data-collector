import whisper


class WhisperModel:
    def __init__(self) -> None:
        self.model = whisper.load_model("small")

    def detect_language(self, audio_path):
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        return detected_language
