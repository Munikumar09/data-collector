import whisper


class WhisperModel:
    """
    Detect the language of an audio file using the whisper model
    
    Attributes
    ----------
    model: ``str``
        The name of the model to use. The options are "small" and "large"
    device: ``str``
        The device to run the model on. The options are "cpu" and "cuda"
    """
    def __init__(self, model: str = "small", device: str = "cpu") -> None:
        self.device = device
        self.model = whisper.load_model(model).to(device)

    def detect_language(self, audio_path:str):
        """ 
        Detect the language of the audio file at the given path using the whisper model
        
        Parameters
        ----------
        audio_path: ``str``
            The path to the audio file to detect the language
        
        Returns
        -------
        ``str``
            The detected language of the audio file
        
        """
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        return detected_language
