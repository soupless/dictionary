import json
import logging
from datetime import datetime
from pathlib import Path

from typing import Any

__all__ = [
    "NotADictionaryError",
    "new",
    "validate_dict",
    "read_json",
    "save_all_to_file",
    "config_log",
]


class NotADictionaryError(Exception):
    """
    An exception raised when a ``dict`` is invalid to be a ``Dictionary``.
    """

    def __init__(self, path: str, message: str):
        self.message = message
        self.path = path
        super().__init__(self.message)


def new(
    title: str = "", author: str = "", description: str = ""
) -> dict[str, Any]:
    """Return a new dictionary.

    Parameters
    ----------
    title : str, optional
        The title of the dictionary, by default ""
    author : str, optional
        The author of the dictionary, by default ""
    description : str, optional
        The description of the dictionary, by default ""

    Returns
    -------
    dict[str, Any]
        The function returns a ``dict`` object with string keys and ``Any``
        values. Although ``Any`` is the type of the values, the only possible
        types are ``str`` or ``dict``.
    """

    return_value = {
        "title": title,
        "author": author,
        "description": description,
        "revision_date": str(datetime.date(datetime.now())),
        "contents": {},
    }
    return return_value


def validate_dict(content: dict[str, Any]) -> bool:
    """Validates if a ``dict`` is a dictionary.

    Parameters
    ----------
    content : dict[str, Any]
        The object to be validated.

    Returns
    -------
    bool
        Returns ``True`` if it is a dictionary, and is ``False`` otherwise
    """

    __key_list = list(content.keys())
    for key in ["title", "author", "description", "revision_date", "contents"]:
        if not (key in __key_list):
            return False
        __key_list.remove(key)
    return False if len(__key_list) > 0 else True


def read_json(path: str) -> dict[str, Any]:
    """Reads and parses JSON files as dictionaries.

    Parameters
    ----------
    path : str
        The path of the JSON file.

    Returns
    -------
    dict[str, Any]
        The dictionary content as a ``dict``.

    Raises
    ------
    JSONDecodeError
        Raised when the file cannot be parsed as JSON.

    NotADictionaryError
        Raised when the file cannot be parsed as a dictionary.
    """
    file_contents: dict[str, Any]
    file_path = Path(path)

    if not file_path.exists:
        raise FileNotFoundError

    with open(path, "r") as f:
        contents = f.read()
        file_contents = json.loads(contents)

        if not (validate_dict(file_contents)):
            raise NotADictionaryError(
                path, "JSON content invalid to be dictionary"
            )

    return file_contents


# TODO: Find a save-by-appending method for large files


def save_all_to_file(content: dict[str, Any], path: str) -> None:
    """Saves the entire content to the JSON file.

    Parameters
    ----------
    content : dict[str, Any]
        The content to be saved.
    path : str
        The path of the JSON file.
    """
    with open(path, "w") as f:
        f.write(json.dumps(content, indent=4, sort_keys=True))
    return None


def config_log(path: str) -> None:
    """Sets the configuration for the logging module.

    Parameters
    ----------
    path : str
        The path of the dictionary file.
    """

    file_details = Path(path)
    file_name = file_details.stem
    file_dir = str(file_details.parent)

    logging.basicConfig(
        filename=f"{file_dir}\\{file_name}.log",
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=logging.DEBUG,
    )

    return None


def date() -> str:
    """Returns the current date.

    Returns
    -------
    str
        The string representation of ``datetime.now().date()``.
    """
    return datetime.now().date().__str__()


def time() -> str:
    """Returns the current time.

    Returns
    -------
    str
        The string representation of ``datetime.now().time()``.
    """
    return str(datetime.now().time()).split(".")[0]


def date_time() -> str:
    """Returns the current date and time.

    Returns
    -------
    str
        The string representation of ``datetime.now()``.
    """
    return datetime.now().isoformat(sep=" ", timespec="seconds")