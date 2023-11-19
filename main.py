from app.audio_processor import AudioProcessor
from app.data_retrival import DataRetrieval
from app.whisper_model import WhisperModel
from app.data_validator import DataValidator
from app.nemo_model import NemoASR
from app.db.db_functions import filter_and_insert_videos
from app.db.connection import create_db_and_tables
import click

import logging
import sys
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s:%(message)s",
)


@click.command()
@click.option(
    "--search_queries",
    required=True,
    help="Search query file that has queries to search for videos on YouTube",
)
@click.option(
    "--is_file",
    default=False,
    is_flag=True,
    help="If search_query_file is a file or a string",
)
@click.option(
    "--device",
    default="cpu",
    help="Device to run the models on. Choose from 'cpu' or 'cuda'",
)
@click.option(
    "--max_pages",
    default=1,
    help="Maximum number of pages to search for videos. Each page has 20 videos",
)
@click.option(
    "--language",
    default="hindi",
    help="Language to search for videos",
)
def main(
    search_queries: str, is_file: bool, device: str, max_pages: int, language: str
):
    logger.info(f"device: {device}\nmax_pages: {max_pages}\nlanguage: {language}")
    
    if is_file:
        with open(search_queries, "r") as f:
            search_queries = f.read().splitlines()

    audio_download_folder = Path(__file__).parent / "speech"
    data_retrieval = DataRetrieval()
    whisper_asr = WhisperModel(device=device)
    nemo_asr = NemoASR(device=device)
    audio_processor = AudioProcessor(whisper_asr, nemo_asr)

    data_validator = DataValidator()

    if isinstance(search_queries, str):
        search_queries = [search_queries]
        
    for search_query in search_queries:
        search_query = f'{search_query}+in+"{language}"'
        search_query = search_query.replace(" ", "+").strip()
        
        audio_query_folder = audio_download_folder / search_query.replace(
            "+", "_"
        ).replace('"', "")
        audio_query_folder.mkdir(exist_ok=True, parents=True)

        logger.info(f"Collecting urls for prompt: {search_query}")
        videos_metadata = data_retrieval.get_video_metadata_with_query(
            search_query, max_pages=max_pages
        )
        
        with open(audio_query_folder / "urls_list.txt", "w") as f:
            video_urls = [metadata.url for metadata in videos_metadata]
            f.write("\n".join(video_urls))
            
        videos_metadata = filter_and_insert_videos(videos_metadata)

        logger.info(f"Collecting transcripts for prompt: {search_query}")
        video_transcription_data = data_retrieval.get_video_transcripts(videos_metadata)

        logger.info(f"total collected transcriptions : {len(video_transcription_data)}")
        logger.info(f"Validating transcripts for prompt: {search_query}")
        valid_transcriptions = data_validator.validate_transcriptions(
            video_transcription_data
        )

        logger.info(f"total valid transcriptions : {len(valid_transcriptions)}")
        logger.info(f"Downloading audio and splitting for prompt: {search_query}")
        audio_processor.download_and_split_audio(
            audio_query_folder, valid_transcriptions, videos_metadata
        )


if __name__ == "__main__":
    create_db_and_tables()
    main()
