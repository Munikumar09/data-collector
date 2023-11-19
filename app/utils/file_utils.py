from pathlib import Path
from typing import Union
import shutil


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


def create_dir(dir_path: Union[str, Path], parents: bool = False):
    """
    Create a directory if it does not exist
    
    Parameters
    ----------
    dir_path: ``Union[str, Path]``
        The path to the directory to be created
    parents: ``bool``, ( default = False )
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
