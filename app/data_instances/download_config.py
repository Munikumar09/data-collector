from dataclasses import dataclass

@dataclass
class DownloadConfig:
    search_queries: str
    is_file: bool
    is_channel_ids: bool
    percent_match: int
    device: str
    max_pages: int
    language: str
    dst_folder_name: str
    download_audio_format: str
    