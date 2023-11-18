from app.audio_processor import AudioProcessor
from app.data_retrival import DataRetrieval
from app.models import WhisperModel
from app.data_validator import DataValidator
from app.nemo import NemoASR
from app.trascription_utils import calculate_similarity, common_ss
from tqdm import tqdm
import json
import logging
import string
import sys
from pathlib import Path
import re

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s:%(message)s",
)


def clean_transcription(transcription):
    # Removing all the punctuations
    punctuations = string.punctuation + "।₹"
    transcription = transcription.translate(
        str.maketrans(punctuations, " " * len(punctuations))
    )
    transcription = re.sub(r"[\u200b\s]+", " ", transcription)

    return transcription.strip()


def main(prompts):
    audio_download_folder = "/home/munikumar-17774/Desktop/data/collect_data/speech"
    data_retrieval = DataRetrieval()
    audio_processor = AudioProcessor()
    whisper_model = WhisperModel()
    nemo_asr = NemoASR()
    data_validator = DataValidator()

    if isinstance(prompts, str):
        prompts = [prompts]
    for prompt in prompts:
        prompt = prompt.replace(" ", "+").strip()

        logger.info(f"Collecting urls for prompt: {prompt}")
        urls = data_retrieval.get_video_urls_with_query(prompt)

        logger.info(f"Collecting transcripts for prompt: {prompt}")
        video_transcription_data = {}
        for url in tqdm(set(urls)):
            transcript = data_retrieval.get_video_transcript(url)
            if transcript:
                video_transcription_data[url] = transcript

        logger.info(f"Validating transcripts for prompt: {prompt}")
        valid_transcription = {}
        for video_url, transcription in tqdm(video_transcription_data.items()):
            clean_transcript = data_validator.validate_transcription(transcription)
            if clean_transcript:
                valid_transcription[video_url] = clean_transcript

        logger.info(f"Downloading audio and splitting for prompt: {prompt}")
        for url, transcription in tqdm(valid_transcription.items()):
            audio_path = Path(
                audio_processor.download_audio(url, audio_download_folder)
            )
            audio_processor.split_audio_and_save_transcription(
                audio_path, transcription
            )
            audio_folder = audio_path.parent / audio_path.stem
            with open(audio_folder / "transcript.json", "r") as f:
                transcript = json.load(f)
            similaty = {}
            for audio_name, yt_text in tqdm(transcript.items()):
                audio_file_path = audio_folder / audio_name
                language = whisper_model.detect_language(str(audio_file_path))
                if language == "hi":
                    nemo_text = nemo_asr.transcribe_audio(str(audio_file_path))[0]
                    yt_text = clean_transcription(yt_text)
                    nemo_text = clean_transcription(nemo_text)
                    sub_string = common_ss(yt_text, nemo_text)
                    percent_match = calculate_similarity(yt_text, nemo_text, sub_string)
                    similaty[audio_name] = {
                        "normal": yt_text,
                        "nemo": nemo_text,
                        "sub_string": sub_string,
                        "percent_match": percent_match,
                    }
            with open(audio_folder / "text_similarity.json", "w") as f:
                json.dump(similaty, f, ensure_ascii=False)


if __name__ == "__main__":
    prompt = 'cricket in "hindi"'
    main(prompt)
