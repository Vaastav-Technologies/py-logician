#!/usr/bin/env python3
# coding=utf-8

"""
Important utilities for std python logging library.
"""

import logging
from logging import Handler
from typing import IO
from collections import defaultdict

from vt.utils.errors.warnings import vt_warn
from logician.stdlog.constants import LOG_LVL as L, LOG_FMT as F, LOG_STR_LVL as S


def level_name_mapping() -> dict[L, S]:
    """
    :return: level -> name mapping from std lib.
    """
    return {
        level: logging.getLevelName(level)
        for level in sorted(logging.getLevelNamesMapping().values())
    }


class TempSetLevelName:
    def __init__(
        self,
        level: L,
        level_name: S | None,
        reverting_lvl_name: S,
        no_warn: bool = False,
    ):
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
            if self.level_name.strip() == "":
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


def add_new_formatter(stream: IO, fmt: F) -> logging.StreamHandler:
    """
    Get a handler for ``stream`` with formatter conforming ``fmt`` param.

    >>> import sys

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
