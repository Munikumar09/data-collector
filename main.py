from app.audio_processor import AudioProcessor
from app.data_retrival import DataRetrieval
from app.whisper_model import WhisperModel
from app.data_validator import DataValidator
from app.nemo_model import NemoASR
from app.data_instances.download_config import DownloadConfig
from app.db.db_functions import filter_and_insert_videos
from app.db.connection import create_db_and_tables
from app.utils.file_utils import create_dir,remove_files_with_pattern
import hydra
from omegaconf import DictConfig, OmegaConf

import logging
import sys
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s:%(message)s",
)


@hydra.main(config_path="./", config_name="download_config",version_base=None)
def main(cfg: DictConfig):
    download_config = DownloadConfig(**OmegaConf.to_container(cfg))
    logger.info(
        f"device: {download_config.device}\nmax_pages: {download_config.max_pages}\nlanguage: {download_config.language}"
    )
    search_queries = download_config.search_queries
    # Prepare the queries to search for videos
    if download_config.is_file:
        with open(search_queries, "r") as f:
            search_queries = f.read().splitlines()
    file_path=Path(__file__).parent

    audio_download_folder = Path(download_config.dst_folder_name)
    
    # Initialize the data retrieval, whisper model, nemo model, audio processor and data validator
    data_retrieval = DataRetrieval()
    whisper_asr = WhisperModel(
        model=download_config.whisper_model_or_path, device=download_config.device
    )
    nemo_asr = NemoASR(
        model_name=download_config.nemo_model_or_path, device=download_config.device
    )
    audio_processor = AudioProcessor(whisper_asr, nemo_asr)
    data_validator = DataValidator()

    if isinstance(search_queries, str):
        search_queries = [download_config.search_queries]
    processed_queries_path=file_path/"processed_queries.txt"
    if processed_queries_path.exists():
        with open(file_path/"processed_queries.txt", "r") as f:
            processed_queries = f.read().splitlines()
        for query in processed_queries:
            if query in search_queries:
                search_queries.remove(query)

    # Collect the video metadata, transcriptions for each query.
    # Download the audio and split it into chunks and save the transcription along with the metadata
    for search_query in search_queries:
        logger.info(f"Collecting urls for query or channel id: {search_query}")
        if download_config.is_channel_ids:
            audio_query_folder = audio_download_folder / search_query
            videos_metadata = data_retrieval.get_video_metadata_with_channel_id(
                search_query
            )
        else:
            original_query=search_query
            search_query = search_query.lower().strip()
            search_query = search_query.replace(" ", "+").strip()
            audio_query_folder = audio_download_folder / search_query.replace(
                "+", "_"
            ).replace('"', "")
            logger.info(f"Collecting urls for query: {search_query}")
            videos_metadata = data_retrieval.get_video_metadata_with_query(
                search_query, max_pages=download_config.max_pages
            )
            
        create_dir(audio_query_folder)

        with open(audio_query_folder / "urls_list.txt", "w") as f:
            video_urls = [metadata.url for metadata in videos_metadata]
            f.write("\n".join(video_urls))
        logger.info(f"total collected urls before filtering : {len(videos_metadata)}")
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
            audio_query_folder,
            valid_transcriptions,
            videos_metadata,
            download_config.download_audio_format,
            download_config.percent_match,
        )
        
        with open(file_path/"processed_queries.txt", "a+") as f:
            f.write(original_query+"\n")
        remove_files_with_pattern(audio_query_folder,download_config.download_audio_format)
        remove_files_with_pattern(audio_query_folder,".part")
        

if __name__ == "__main__":
    create_db_and_tables()
    main()
