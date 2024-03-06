from pydub import AudioSegment
import json
from pathlib import Path
import yt_dlp
from typing import Dict, List, Union, Optional
from app.data_instances.video_meta import VideoMetaData
from tqdm import tqdm
from app.utils.transcription_utils import (
    calculate_similarity,
    find_longest_common_substring,
    clean_transcription,
)
from app.utils.common_utils import save_json
from app.utils.file_utils import create_dir
from app.db.db_functions import insert_video_metadata
from app.models.speech_language_detection.speech_language_detection import (
    SpeechLanguageDetection,
)
from app.models.asr.asr import ASR


class AudioProcessor:
    """
    AudioProcessor class to download the audio and split it into chunks and save the transcription

    Attributes
    ----------
    speech_language_detector: ``SpeechLanguageDetection``
        SpeechLanguageDetection object to detect the language of the audio
    asr: ``ASR``
        ASR object to transcribe the audio
    """

    def __init__(
        self, speech_language_detector: SpeechLanguageDetection, asr: ASR
    ) -> None:
        self.speech_language_detector = speech_language_detector
        self.asr = asr

    def download_audio(
        self, url: str, root_path: Union[str, Path], format: str
    ) -> Optional[Path]:
        """
        Download audio from youtube url and save it to root_path

        Parameters
        ----------
        url: ``str``
            Youtube url of the video to download
        root_path: ``Union[str, Path]``
            Path to save the downloaded audio

        Returns
        -------
        ``Path``
            Path to the downloaded audio
        """
        print(f"Downloading audio from {url}")
        if isinstance(root_path, str):
            root_path = Path(root_path)

        download_path = root_path / url.split("=")[1]
        audio_file_path = download_path.with_suffix(f".{format}")

        if audio_file_path.exists():
            return audio_file_path

        ydl_opts = {
            "format": "m4a/bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
            "outtmpl": str(download_path),
            "quiet": True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
        except Exception as e:
            print(f"Exception occurred while downloading audio: {e}")
            return None

        return audio_file_path

    def split_audio_and_save_transcription(
        self,
        audio_path: Path,
        audio_chunk_save_folder: str,
        transcription_data: List[Dict[str, str]],
    ):
        """
        Split the audio into chunks and save the transcription of each chunk in a json file

        Parameters
        ----------
        audio_path: ``Path``
            Path to the audio file to split into chunks
        transcription_data: ``List[Dict[str, str]]``
            A list of dictionaries containing text and time of the audio
        """
        transcript = {}
        audio = AudioSegment.from_mp3(audio_path)
        audio = audio.set_channels(1)
        audio_path = Path(audio_path)
        create_dir(audio_chunk_save_folder)

        for data in transcription_data:
            start_time = data["start"]
            end_time = data["start"] + data["duration"]
            audio_chunk = audio[start_time * 1000 : end_time * 1000]
            file_name = f"{start_time}_{end_time}.mp3"
            audio_chunk.export(f"{audio_chunk_save_folder}/{file_name}", format="mp3")
            transcript[file_name] = data["text"]

        with open(f"{audio_chunk_save_folder}/transcript.json", "w") as f:
            json.dump(transcript, f, ensure_ascii=False)

    def validate_transcriptions(
        self,
        transcription_data: Dict[str, List[Dict[str, str]]],
        audio_folder: Path,
        video_metadata: Optional[VideoMetaData],
        threshold: int = 20,
    ):
        """
        Validate the transcriptions of the audios whether they are in Hindi or not.
        Using Whisper model to detect the language of the audio and Nemo model to transcribe the audio.
        Matching the transcriptions of the audio from Whisper and Nemo model and saving the similarity using Common Substring algorithm.

        Parameters
        ----------
        transcription_data: ``Dict[str, List[Dict[str, str]]]``
            A dictionary of audio name and its transcription
        audio_folder: ``Path``
            Path to the folder containing the audio files
        video_metadata: ``Optional[VideoMetaData]``
            VideoMetaData object of the video
        threshold: ``int``, ( default = 20 )
            Threshold to consider the similarity between the transcriptions
        """

        similarity = {}
        req_langugage_file_count = 0
        for audio_name, yt_text in tqdm(transcription_data.items()):
            try:
                if yt_text.strip() == "":
                    continue

                audio_file_path = audio_folder / audio_name
                language = self.speech_language_detector.detect_language_from_file(str(audio_file_path))

                if language.lower() == "hi":
                    req_langugage_file_count += 1
                    nemo_text = self.asr.transcribe_audio_file(str(audio_file_path))[0]
                    yt_text = clean_transcription(yt_text)
                    nemo_text = clean_transcription(nemo_text)
                    sub_string = find_longest_common_substring(yt_text, nemo_text)
                    percent_match = calculate_similarity(yt_text, nemo_text, sub_string)

                    if percent_match > threshold:
                        similarity[audio_name] = {
                            "normal": yt_text,
                            "nemo": nemo_text,
                            "sub_string": sub_string,
                            "percent_match": percent_match,
                        }
            except Exception:
                print(f"Exception occurred while processing audio: {audio_name}")

        if similarity:
            save_json(
                similarity, audio_folder / "text_similarity.json", ensure_ascii=False
            )
            if video_metadata:
                insert_video_metadata(video_metadata)
        else:
            print(f"files with hindi language are : {req_langugage_file_count} in {audio_folder}")

    def download_and_split_audio(
        self,
        root_audio_dir: Union[str, Path],
        valid_transcription_data: Dict[str, List[Dict[str, str]]],
        videos_metadata: Optional[List[VideoMetaData]],
        format: str,
        threshold: int = 20,
    ):
        """
        Download the audio and split it into chunks and save the transcription of each chunk in a json file and validate the transcriptions.

        Parameters
        ----------
        root_audio_dir: ``Union[str, Path]``
            Path to save the downloaded audio
        valid_transcription_data: ``Dict[str, List[Dict[str, str]]]``
            A dictionary of video URL and its valid transcription
        videos_metadata: ``Optional[List[VideoMetaData]]``
            A list of VideoMetaData objects for each video
        format: ``str``
            Format to download the audio
        threshold: ``int``, ( default = 20 )
            Threshold to consider the similarity between the transcriptions
        """
        if isinstance(root_audio_dir, str):
            root_audio_dir = Path(root_audio_dir)

        for video_url, transcription_data in valid_transcription_data.items():
            video_id = video_url.split("=")[-1]

            if (root_audio_dir / video_id).exists():
                continue

            audio_path = self.download_audio(video_url, root_audio_dir, format)

            if audio_path:
                for transcription_type, transcriptions in transcription_data.items():
                    if transcriptions:
                        audio_folder = (
                            audio_path.parent / audio_path.stem / transcription_type
                        )
                        self.split_audio_and_save_transcription(
                            audio_path, audio_folder, transcriptions
                        )

                        with open(audio_folder / f"transcript.json", "r") as f:
                            transcriptions = json.load(f)

                        video_metadata = None

                        if videos_metadata:
                            for video_metadata in videos_metadata:
                                if video_metadata.video_id == video_id:
                                    break

                        self.validate_transcriptions(
                            transcriptions, audio_folder, video_metadata, threshold
                        )
