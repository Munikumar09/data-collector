from pydub import AudioSegment
from typing import Union
import json
from pathlib import Path
import yt_dlp


class AudioProcessor:
    def download_audio(self, url: str, root_path: Union[str, Path]):
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
        if isinstance(root_path, str):
            root_path = Path(root_path)
        file_name = url.split("=")[1]
        download_path = root_path / file_name
        audio_file_path = download_path.with_suffix(".mp3")
        if audio_file_path.exists():
            return audio_file_path
        
        ydl_opts = {
            "format": "m4a/bestaudio/best",
            # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
            "postprocessors": [
                {  # Extract audio using ffmpeg
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
            "outtmpl": str(download_path),
        }
        print(f"Downloading audio from {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
        return audio_file_path

    def split_audio_and_save_transcription(self, audio_path, transcription_data):
        transcript = {}
        audio = AudioSegment.from_mp3(audio_path)
        audio = audio.set_channels(1)
        audio_path = Path(audio_path)
        audio_folder = audio_path.parent / audio_path.stem
        audio_folder.mkdir(parents=True, exist_ok=True)
        for data in transcription_data:
            start_time = data["start"]
            end_time = data["start"] + data["duration"]
            audio_chunk = audio[start_time * 1000 : end_time * 1000]
            file_name = f"{start_time}_{end_time}.mp3"
            audio_chunk.export(f"{str(audio_folder)}/{file_name}", format="mp3")
            transcript[file_name] = data["text"]
        with open(f"{str(audio_folder)}/transcript.json", "w") as f:
            json.dump(transcript, f, ensure_ascii=False)

        return None
