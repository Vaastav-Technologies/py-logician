#!/usr/bin/env python3
# coding=utf-8

"""
Important utilities for std python logging library.
"""
import logging
import sys
from logging import Handler
from typing import TextIO, IO
from collections import defaultdict

from vt.utils.errors.warnings import vt_warn

from logician.formatters import LogLevelFmt
from logician.stdlog.formatters import StdLogAllLevelSameFmt


def level_name_mapping() -> dict[int, str]:
    """
    :return: level -> name mapping from std lib.
    """
    return {level: logging.getLevelName(level) for level in
            sorted(logging.getLevelNamesMapping().values())}


class TempSetLevelName:
    def __init__(self, level: int, level_name: str | None, reverting_lvl_name: str, no_warn: bool = False):
        """
        Set the log level name temporarily and then revert it back to the ``reverting_lvl_name``.

        :param level: The log level to set name to.
        :param level_name: Level name to set the level to.
        :param reverting_lvl_name: The log level name to revert to when operation finishes.
        :param no_warn: A warning is shown if the supplied ``level_name`` is strip-empty. This warning can be suppressed
            by setting ``no_warn=True``.
        """
        self.level = level
        self.level_name = level_name
        self.reverting_lvl_name = reverting_lvl_name
        self.no_warn = no_warn
        self.original_level_name = logging.getLevelName(level)

    def __enter__(self):
        if self.level_name is not None:
            if self.level_name.strip() == '':
                self.warn_user()
            else:
                logging.addLevelName(self.level, self.level_name)

    def warn_user(self):
        """
        A warning is shown if the supplied ``level_name`` is strip-empty. This warning can be suppressed
            by setting ``no_warn=True`` in ctor.
        """
        if not self.no_warn:
            self._warn_user()

    def _warn_user(self):
        vt_warn(f"Supplied log level name for log level {self.level} is empty.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.level_name:
            logging.addLevelName(self.level, self.reverting_lvl_name)
        else:
            logging.addLevelName(self.level, self.original_level_name)


def get_first_non_none[T](lst: list[T | None], default: T | None = None) -> T | None:
    """
    Get first non-``None`` item from the list ``lst`` else ``default``.

    Examples:

      * Return the default if all values are ``None``:

        >>> get_first_non_none([None, None, None], 5)
        5

      * default can be ``None``:

        >>> get_first_non_none([None, None], None)

      * first non-``None`` is returned:

        >>> get_first_non_none([None, None, 2, None, 5], 9)
        2

      * default is returned when empty-list is supplied:

        >>> get_first_non_none([], "some str")
        'some str'

        >>> get_first_non_none([], None) # None returned as default is None

        >>> get_first_non_none([]) # None returned as default is None

    :param lst: list of values.
    :param default: value to return if list consists of all ``None``s.
    :return: first non ``None`` value or ``default`` if all ``None`` are encountered.
    """
    for lst_elem in lst:
        if lst_elem is not None:
            return lst_elem
    return default


def form_stream_handlers_map(logger: logging.Logger) -> dict[IO, list[Handler]]:
    """
    :param logger: the logger whose stream->list[handlers] mapping is to be obtained.
    :return: stream->list[handlers] mapping for the supplied logger.
    """
    stream_handler_map: dict[IO, list[Handler]] = defaultdict(list)
    """
    Map of logger's stream and its handlers.
    """
    # Create a mapping of stream->list[handlers for that stream]
    for handlr in logger.handlers:
        if isinstance(handlr, logging.StreamHandler):
            stream_handler_map[handlr.stream].append(handlr)
    return stream_handler_map


def add_new_formatter(stream: IO, fmt: str) -> logging.StreamHandler:
    """
    Get a handler for ``stream`` with formatter conforming ``fmt`` param.

    Examples:

    >>> h = add_new_formatter(sys.stdout, "%(name)s")
    >>> assert h.formatter._fmt == "%(name)s"   # type: ignore[attr-defined]

    :param stream: A new ``logging.StreamHandler`` will be created for this stream.
    :param fmt: A formatter conforming to ``fmt`` will be set for ``stream``.
    :return: a new handler with the formatter set to ``fmt``.
    """
    _handlr = logging.StreamHandler(stream=stream)  # type: ignore[arg-type]
    _handlr.setFormatter(logging.Formatter(fmt=fmt))
    return _handlr
