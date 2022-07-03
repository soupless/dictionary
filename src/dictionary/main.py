from __future__ import annotations
from enum import Enum

import logging
import re
from typing import Any
from pathlib import Path

from jellyfish import damerau_levenshtein_distance

from . import file_ops


class SearchMode(Enum):
    """Search modes for the ``search`` method of the class ``Dictionary``."""

    Exact = 0
    SubStr = 1
    Approx = 2


class InfoType(Enum):
    """Information types for the ``information_on`` method of the class
    ``Dictionary``."""

    Definitions = 0
    References = 1


class Dictionary(dict):
    def __init__(
        self,
        path: str,
        title: str = "",
        author: str = "",
        description: str = "",
    ) -> None:
        """Initialization of the ``Dictionary`` class.

        The arguments ``title``, ``author``, and ``description`` are used only
        if ``path`` is left blank.

        Parameters
        ----------
        path : str
            The path of the dictionary file
        title : str, optional
            The title of the new dictionary, by default ""
        author : str, optional
            The author of the new dictionary, by default ""
        description : str, optional
            The description of the new dictionary, by default ""
        """
        file_content: dict[str, Any]
        path_details = Path(path)

        if path_details.exists():
            if not path_details.is_file():
                raise FileNotFoundError
            file_content = file_ops.read_json(path)
        else:
            file_content = file_ops.new(title, author, description)

        for key, value in file_content.items():
            assert isinstance(key, str)
            assert isinstance(value, (str, dict))

        self.__title: str = file_content.pop("title")
        self.__author: str = file_content.pop("author")
        self.__description: str = file_content.pop("description")
        self.__revision_date: str = file_content.pop("revision_date")
        self.__path = path

        super().__init__(file_content["contents"])

        self.__edited = False

        file_ops.config_log(path)

        if not path_details.is_file():
            logging.info(f"Created new dictionary {path_details.parts[-1]}.")

        logging.info(f"Initialized {path}.")

    def __delitem__(self, __v: str) -> None:
        """An invalidation of the inherited ``__delitem__`` method to
        avoid data destruction."""
        logging.warning(f"Attempted to use __delitem__ on {self.path}")
        raise NotImplementedError

    def pop(self, __k, __d=None) -> Any:
        """An invalidation of the inherited ``pop`` method to avoid data
        destruction."""

        raise NotImplementedError

    def __setitem__(self, __k, __v) -> None:
        def validate_kwcontent(__v: dict[Any, Any]) -> bool:
            VALID_KEYS = ("definitions", "references")
            return all(key in VALID_KEYS for key in __v) and all(
                key in __v for key in VALID_KEYS
            )

        if not isinstance(__k, str):
            raise NotImplementedError

        if __k in self:
            raise NotImplementedError
        else:
            if validate_kwcontent(__v):
                super().__setitem__(__k, __v)
            else:
                raise NotImplementedError

    def popitem(self) -> tuple[str, Any]:
        """An invalidation of the inherited ``popitem`` method to avoid data
        destruction."""
        logging.warning(f"Attempted to use ``pop`` method on {self.path}")
        raise NotImplementedError

    def clear(self) -> None:
        """An invalidation of the inherited ``clear`` method to avoid data
        destruction."""
        logging.warning("Attempted to clear the dictionary")
        raise NotImplementedError

    @property
    def title(self) -> str:
        """The title of the dictionary."""
        return self.__title

    @property
    def author(self) -> str:
        """The author of the dictionary."""
        return self.__author

    @property
    def description(self) -> str:
        """The description of the dictionary."""
        return self.__description

    @property
    def revision_date(self) -> str:
        """The date of the last revision of the dictionary."""
        return self.__revision_date

    @property
    def edited(self) -> bool:
        """An indicator whether the dictionary was edited."""
        return self.__edited

    @property
    def path(self) -> str:
        """The path of the dictionary file."""
        return self.__path

    def _convert_to_dict(self) -> dict[str, Any]:
        """Converts the dictionary into a proper ``dict`` object.

        Returns
        -------
        dict[str, Any]
            The entire dictionary data into a ``dict``.
        """
        return {
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "revision_date": self.revision_date,
            "contents": self,
        }

    def save(self) -> None:
        """Saves the dictionary to its associated file, if it was edited."""
        if self.edited:
            self.__revision_date = file_ops.date()
            file_ops.save_all_to_file(self._convert_to_dict(), self.path)
        self.__edited = False
        logging.info(f"Saved {Path(self.path).parts[-1]}.")

    def information_on(
        self, keyword: str, about: InfoType
    ) -> list[str] | None:
        """Returns the information requested for a given keyword, if it exists.

        Parameters
        ----------
        keyword : str
            The string to be searched.
        about : InfoType
            The type of information requested from the given keyword.

        Returns
        -------
        list[str] | bool | None
            Returns a value of type ``list[str]`` if definitions or references
            are requested, or ``bool`` if the case-sensitivity of the keyword
            is requested. Otherwise, ``None`` is returned.
        """
        if keyword in self:
            return self[keyword][about.name.lower()]
        return None

    def add(
        self,
        keyword: str,
        definition: str = "",
        reference: str = "",
    ) -> None:
        """Adds content to the dictionary. If the keyword already exists, the
        given definition and/or reference will be added instead.

        Parameters
        ----------
        keyword : str
            The keyword whose contents are to be added.
        definition : str, optional
            The definition of the keyword, by default ``''``
        reference : str, optional
            The reference of the keyword, by default ``''``
        """

        if not (definition or reference):
            raise ValueError("No passed content")

        if keyword in self:
            if definition:
                self[keyword]["definitions"].append(definition)
                logging.info(
                    f"Added the definition '{definition}' to the keyword"
                    f" '{keyword}'."
                )
            if reference:
                self[keyword]["references"].append(reference)
                logging.info(
                    f"Added the reference '{reference}' to the keyword"
                    f" '{keyword}'."
                )

        else:
            new_definitions = [definition] if definition else []
            new_references = [reference] if reference else []
            new_entry: dict[str, bool | list[str]] = {
                "definitions": new_definitions,
                "references": new_references,
            }
            self[keyword] = new_entry

            logging.info(f"Added the keyword '{keyword}' to the dictionary.")

            if definition:
                logging.info(
                    f"Added the definition '{definition}' to the keyword "
                    f"'{keyword}'."
                )

        self.__edited = True

    def remove(
        self, keyword: str, definition: str = "", reference: str = ""
    ) -> None:
        """Removes content from the dictionary.

        If both definition and reference passed are blank, the keyword itself
        is removed. As such, if at least the definition or the reference are
        not blank, only the non-blank entries will be removed, if they exist.

        Parameters
        ----------
        keyword : str
            The keyword whose content will be removed.
        definition : str, optional
            The definition to be removed, by default ""
        reference : str, optional
            The reference to be removed, by default ""

        Raises
        ------
        ValueError
            Raised if the content passed is nonexistent.
        """
        if keyword not in self:
            raise ValueError("Nonexistent entry to be removed")

        if definition or reference:
            if definition:
                if definition in self[keyword]["definitions"]:
                    self[keyword]["definitions"].remove(definition)
                else:
                    raise ValueError("Given definition not found")
            if reference:
                if reference in self[keyword]["references"]:
                    self[keyword]["references"].remove(reference)
                else:
                    raise ValueError("Given reference not found")
        else:
            super().__delitem__(keyword)

        self.__edited = True

    def search(
        self,
        keyword: str,
        case_sensitive: bool = False,
        mode: SearchMode = SearchMode.Approx,
        max_results: int = 5,
    ) -> list[tuple[str, int]] | None:

        search_result: list[tuple[str, int]] | None = None

        if max_results < 1:
            raise ValueError("Invalid number of maximum results")
        if not self:
            return None

        keyword = keyword if case_sensitive else keyword.lower()

        if mode == SearchMode.Exact:
            if keyword in (self if case_sensitive else map(str.lower, self)):
                return [(keyword, 0)]

        elif mode == SearchMode.SubStr:
            regex = re.compile(keyword if case_sensitive else f"(?i){keyword}")

            search_result = [
                (key, damerau_levenshtein_distance(keyword, key))
                for key in self
                if regex.search(key)
            ][: max_results]

        elif mode == SearchMode.Approx:
            search_result = [
                (
                    key,
                    damerau_levenshtein_distance(
                        keyword, key if case_sensitive else key.lower()
                    ),
                )
                for key in self
            ][: max_results]

        if search_result is not None:
            search_result.sort(key=lambda t: t[1])

        return search_result
