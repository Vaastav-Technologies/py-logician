#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger formatters.
"""

import logging
import sys
from typing import override, IO, Protocol

from logician.formatters import AllLevelSameFmt, DiffLevelDiffFmt, LogLevelFmt
from logician.stdlog import (
    TIMED_DETAIL_LOG_FMT,
    TRACE_LOG_LEVEL,
    DETAIL_LOG_FMT,
    SHORT_LOG_FMT,
    SHORTER_LOG_FMT,
)
from logician.stdlog.constants import LOG_LVL as L, LOG_FMT as F


class StdLogLevelFmt(LogLevelFmt[L, F], Protocol):
    """
    Base interface for all the level-format mappers for stdlog.
    """

    pass


class StdLogAllLevelSameFmt(StdLogLevelFmt, AllLevelSameFmt[L, F]):
    def __init__(self, fmt: F = SHORTER_LOG_FMT):
        """
        Same std log format for all levels.

        :param fmt: logging format constant for all std log levels.
        """
        self._fmt = fmt

    @override
    def fmt(self, level: L) -> F:
        return self._fmt


class StdLogAllLevelDiffFmt(StdLogLevelFmt, DiffLevelDiffFmt[L, F]):
    DEFAULT_LOGGER_DICT: dict[L, F] = {
        TRACE_LOG_LEVEL: TIMED_DETAIL_LOG_FMT,
        logging.DEBUG: DETAIL_LOG_FMT,
        logging.INFO: SHORT_LOG_FMT,
        logging.WARN: SHORTER_LOG_FMT,
    }
    """
    Different log formats for different log levels.
    """

    def __init__(self, fmt_dict: dict[L, F] | None = None):
        """
        Specify how different log levels should impact the logging formats.

        For e.g.::

            - least verbose ERROR level.
            ERROR: an error occurred.

            - less verbose INFO level.
            logger.name: INFO: some information

            - verbose DEBUG level.
            logger.name: DEBUG: [filename.py - func()]: some debug info

            - most verbose TRACE level.
            2025-04-03 20:59:39,418: TRACE: [filename.py:218 - func()]: some trace info

        provides immediately-upper registered level if an unregistered level is queried.

        :param fmt_dict: level -> format dictionary. Defaults to
            ``StdLogAllLevelDiffFmt.DEFAULT_LOGGER_DICT`` when ``None`` or an empty dict is provided.
        """
        self._fmt_dict = (
            fmt_dict if fmt_dict else StdLogAllLevelDiffFmt.DEFAULT_LOGGER_DICT
        )

    @override
    def fmt(self, level: L) -> F:
        final_level = (
            level if level in self._fmt_dict else self.next_approx_level(level)
        )
        return self._fmt_dict[final_level]

    @override
    def next_approx_level(self, missing_level: L) -> L:
        """
        :param missing_level: A level that was not registered in the logger.
        :return: immediately-upper registered level if a ``missing_level`` is queried.
        """
        max_level = max(self._fmt_dict)
        if missing_level >= max_level:
            return max_level

        for level in sorted(self._fmt_dict.keys()):
            if level > missing_level:
                return level
        return max_level


def stderr_all_lvl_same_fmt(fmt: F | None = None) -> dict[IO, StdLogLevelFmt]:
    """
    Examples:

      * ``SHORTER_LOG_FMT`` is used when the ``fmt`` param is not supplied:

        >>> fmt_dict = stderr_all_lvl_same_fmt()
        >>> assert sys.stderr in fmt_dict
        >>> assert fmt_dict[sys.stderr].fmt(logging.DEBUG) == SHORTER_LOG_FMT

      * Supplied format is used when ``fmt`` is supplied:

        >>> fmt_dict = stderr_all_lvl_same_fmt("%(name)s")
        >>> assert sys.stderr in fmt_dict
        >>> assert fmt_dict[sys.stderr].fmt(logging.FATAL) == "%(name)s"

    :param fmt: the format required for all levels
    :return: stderr->same-format-for-all-levels dict.
    """
    if fmt is not None:
        return {sys.stderr: StdLogAllLevelSameFmt(fmt)}
    return {sys.stderr: StdLogAllLevelSameFmt()}


STDERR_ALL_LVL_SAME_FMT: dict[IO, StdLogLevelFmt] = stderr_all_lvl_same_fmt()
"""
Maps ``sys.stderr`` to same logging format for all levels.
"""

STDERR_ALL_LVL_DIFF_FMT: dict[IO, StdLogLevelFmt] = {
    sys.stderr: StdLogAllLevelDiffFmt()
}
"""
Maps ``sys.stderr`` to different logging format for all levels.
"""
