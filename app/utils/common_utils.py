import json
from typing import Any, Union, Iterator, List
from pathlib import Path
from app.utils.file_utils import create_dir, resolve_path
import csv
import os
import shutil


def save_json(data: Any, save_path: Union[str, Path], ensure_ascii: bool = True):
    """
    Save the data as a json file to the given path

    Parameters
    ----------
    data: ``Any``
        The data to save as a json file
    save_path: ``Union[str, Path]``
        The path to save the json file
    ensure_ascii: ``bool``, ( default = True )
        Flag to ensure that the data is in ascii format
    """
    save_path = Path(save_path)
    create_dir(save_path.parent, parents=True)

    with open(save_path, "w") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii)


def load_json(file_path: Union[str, Path]):
    """
    Load the json file from the given path

    Parameters
    ----------
    file_path: ``Union[str, Path]``
        The path to load the json file from

    Returns
    -------
    ``Any``
        The data loaded from the json file
    """
    resolve_path(file_path)
    with open(file_path, "r") as f:
        return json.load(f)


def read_csv(
    csv_filepath: Union[str, Path], as_list: bool = True
) -> Iterator[Union[str, List[str]]]:
    """
    Reads the `csv_filepath` and return the row as either List or str

    Parameters
    ----------
    csv_filepath: ``Union[str, Path]``
        Input CSV file path
    as_list: ``bool``, ( default = True )
        Flag that denotes whether to return the row as `list` or `string`

    Returns
    -------
    ``Union[str, List[str]]``
    """
    with open(csv_filepath, "r") as fp:
        if as_list:
            for row in csv.reader(fp):
                yield row
        else:
            for line in fp:
                yield line


def delete_pycache(root_dir: str, folder_name: str):
    """
    Deletes a folder and its contents from a given root directory.

    Parameters
    ----------
    root_dir: `str`
        The path of the root directory to traverse.
    folder_name: `str`
        The name of the folder to delete.

    Raises
    ------
    OSError:
        If the folder cannot be deleted due to permission or other errors.

    Examples
    --------
    >>> delete_folder("Users/Admin/Documents", "pycache")
        Deleting Users/Admin/Documents_pycache_
        Deleting Users/Admin/Documents/project_pycache_
    """
    # Traverse through the directory tree
    for dirpath, dirnames, _ in os.walk(root_dir):
        # Check if the specified folder exists in the current directory
        if folder_name in dirnames:
            # Get the full path of the pycache folder
            pycache_folder_path = os.path.join(dirpath, folder_name)

            # Print the path of the folder being deleted
            print(f"Deleting {pycache_folder_path}")

            # Delete the pycache folder and its contents
            shutil.rmtree(pycache_folder_path)
