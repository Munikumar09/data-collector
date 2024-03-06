from pathlib import Path
from typing import Union, List
import shutil
import json


def resolve_path(path: Union[str, Path]):
    """
    Find the given path exists or not and return the path object

    Parameters
    ----------
    path: ``Union[str,Path]``
        The path to resolve

    Returns
    -------
    ``Path``
        The resolved path object
    """
    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"{path} is not found")

    return path


def remove_files_with_pattern(base_path: Union[str, Path], pattern: str):
    """
    Remove files with the given pattern from the base path

    Parameters
    ----------
    base_path: ``Union[str, Path]``
        The base path to remove files
    pattern: ``str``
        The pattern to remove files
    """
    if isinstance(base_path, str):
        base_path = Path(base_path)

    if not pattern.startswith("."):
        pattern = f".{pattern}"
    pattern = f"*{pattern}"

    for file in base_path.glob(pattern):
        if file.is_file():
            file.unlink()


def create_dir(dir_path: Union[str, Path], parents: bool = True):
    """
    Create a directory if it does not exist

    Parameters
    ----------
    dir_path: ``Union[str, Path]``
        The path to the directory to be created
    parents: ``bool``, ( default = True )
        Flag to create parent directories if they do not exist
    """
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)

    if not dir_path.exists():
        dir_path.mkdir(parents=parents, exist_ok=True)


def remove_dir(dir_name: Union[str, Path]):
    """
    Delete an existing directory

    Parameters
    ----------
    dir_name: ``str``
        Directory name to be deleted
    """
    if isinstance(dir_name, str):
        dir_name = Path(dir_name)

    if dir_name.exists():
        shutil.rmtree(dir_name)


def get_total_duration_from_transcription_file(
    transcription_file, audio_file_format="mp3", percent_based=False, low=30, high=100
) -> float:
    """
    Get the total duration of the audio from the transcription file

    Parameters
    ----------
    transcription_file: ``Union[str, Path]``
        The path to the transcription file

    Returns
    -------
    ``float``
        The total duration of the audio in seconds
    """
    total_duration = 0
    with open(transcription_file, "r") as f:
        transcript = json.load(f)
    for audio_file_name, transcriptions in transcript.items():
        audio_file_name = audio_file_name.replace(f".{audio_file_format}", "")
        start_time = float(audio_file_name.split("_")[0])
        end_time = float(audio_file_name.split("_")[1])
        duration = end_time - start_time
        if percent_based and "percent_match" in transcriptions:
            if (
                transcriptions["percent_match"] >= low
                and transcriptions["percent_match"] <= high
            ):
                total_duration += duration
        else:
            total_duration += duration
    return total_duration


def filter_unqiue_files(transcription_files: List[str]) -> list:
    unique_files = set()
    for transcript_file in transcription_files:
        if "manual" in str(transcript_file):
            unique_files.add(str(transcript_file))
        else:
            auto_trans = str(transcript_file).replace("auto", "manual")
            if auto_trans not in unique_files:
                unique_files.add(str(transcript_file))

    return list(unique_files)
