from __future__ import annotations

import logging
import re
from typing import Any, Literal
from pathlib import Path

from jellyfish import damerau_levenshtein_distance

from . import file_ops

SEARCH_MODE = Literal["exact", "substr", "approx"]


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

        assert isinstance(file_content, dict)
        for key in file_content:
            value = file_content[key]
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

    def definition_of(self, keyword: str) -> list[str] | None:
        """Returns the list of definitions for a given keyword, if it exists.

        Parameters
        ----------
        keyword : str
            The string to be searched.

        Returns
        -------
        list[str] | None
            The list of the definitions if the keyword exists, otherwise None
        """
        if keyword in self:
            __definition_list: list[str] = self[keyword]["definitions"]
            assert isinstance(__definition_list, list)
            assert all(isinstance(i, str) for i in __definition_list)
            return self[keyword]["definitions"]
        return None

    def add(
        self,
        keyword: str,
        definition: str = "",
        reference: str = "",
        case_sensitive: bool = False,
    ) -> None:
        """Adds content to the dictionary. If the keyword already exists, the
        given definition and/or reference will be added instead.

        The parameter ``case_sensitive`` will only be used if the keyword
        doesn't exist.

        Parameters
        ----------
        keyword : str
            The keyword whose contents are to be added.
        definition : str, optional
            The definition of the keyword, by default ``''``
        reference : str, optional
            The reference of the keyword, by default ``''``
        case_sensitive : bool, optional
            The case sensitivity of the keyword used only when adding a
            nonexistent keyword, by default ``False``
        """

        if not (definition or reference):
            raise ValueError("No passed content")

        if keyword in self:
            if definition:
                self["keyword"]["definitions"].append(definition)
                logging.info(
                    f"Added the definition '{definition}' to the keyword"
                    f" '{keyword}'."
                )
            if reference:
                self["keyword"]["references"].append(reference)
                logging.info(
                    f"Added the reference '{reference}' to the keyword" f" '{keyword}'."
                )

        else:
            new_definitions = [definition] if definition else []
            new_references = [reference] if reference else []
            new_entry: dict[str, bool | list[str]] = {
                "case_sensitive": case_sensitive,
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

    def remove(self, keyword: str, definition: str = "", reference: str = "") -> None:
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
        if keyword in self:
            if definition:
                if definition in self[keyword]["definitions"]:
                    self[keyword]["definitions"].remove(definition)
                else:
                    raise ValueError("Given definition not found")
            elif reference:
                if reference in self[keyword]["references"]:
                    self[keyword]["references"].remove(reference)
                else:
                    raise ValueError("Given reference not found")
            else:
                __new_copy: dict[str, Any] = dict(self)
                del __new_copy[keyword]
                super().__init__(__new_copy)
            self.__edited = True
        else:
            raise ValueError("Nonexistent entry to be removed")

    def search(
        self,
        keyword: str,
        case_sensitive: bool = False,
        mode: SEARCH_MODE = "approx",
        max_results: int = 5,
    ) -> list[tuple[str, int]] | None:

        search_result: list[tuple[str, int]] | None = None

        if max_results < 1:
            raise ValueError("Invalid number of maximum results")
        if not self:
            return None

        if mode == "exact":
            if case_sensitive:
                if keyword in self:
                    search_result = [(keyword, 0)]
            else:
                for key in self:
                    if key.lower() == keyword:
                        search_result = [(key, 0)]
                        break

        elif mode == "substr":
            regex_pattern = keyword if case_sensitive else f"(?i){keyword}"
            regex = re.compile(regex_pattern)

            temp_list: list[tuple[str, int]] = []
            for key in self:
                if regex.search(key) is not None:
                    temp_list.append((key, damerau_levenshtein_distance(keyword, key)))
            temp_list.sort(key=lambda t: t[1])
            search_result = temp_list[: max_results + 1]

        elif mode == "approx":
            search_result = []
            if not case_sensitive:
                keyword = keyword.lower()
            for key in self:
                search_result.append(
                    (
                        key,
                        damerau_levenshtein_distance(
                            keyword, key if case_sensitive else key.lower()
                        ),
                    )
                )
            search_result.sort(key=lambda t: t[1])
            search_result = search_result[: max_results + 1]

        return search_result
