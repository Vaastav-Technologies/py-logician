#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger formatters.
"""
import logging
import sys
from typing import TextIO, override

from vt.utils.logging.logging.formatters import AllLevelSameFmt, DiffLevelDiffFmt, StreamFormatMapper, LogLevelFmt
from vt.utils.logging.logging.std_log import TIMED_DETAIL_LOG_FMT, TRACE_LOG_LEVEL, DETAIL_LOG_FMT, SHORT_LOG_FMT, \
    SHORTER_LOG_FMT


class StdLogAllLevelSameFmt(AllLevelSameFmt):

    def __init__(self, fmt: str = SHORTER_LOG_FMT):
        """
        Same std log format for all levels.

        :param fmt: logging format constant for all std log levels.
        """
        self._fmt = fmt

    @override
    def fmt(self, level: int) -> str:
        return self._fmt


class StdLogAllLevelDiffFmt(DiffLevelDiffFmt):
    DEFAULT_LOGGER_DICT: dict[int, str] = {
        TRACE_LOG_LEVEL: TIMED_DETAIL_LOG_FMT,
        logging.DEBUG: DETAIL_LOG_FMT,
        logging.INFO: SHORT_LOG_FMT,
        logging.WARN: SHORTER_LOG_FMT
    }
    """
    Different log formats for different log levels.
    """

    def __init__(self, fmt_dict: dict[int, str] | None = None):
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
        self._fmt_dict = fmt_dict if fmt_dict else StdLogAllLevelDiffFmt.DEFAULT_LOGGER_DICT

    @override
    def fmt(self, level: int) -> str:
        final_level = level if level in self._fmt_dict else self.next_approx_level(level)
        return self._fmt_dict[final_level]

    @override
    def next_approx_level(self, missing_level: int) -> int:
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


STDERR_ALL_LVL_SAME_FMT: dict[TextIO, LogLevelFmt] = {sys.stderr: StdLogAllLevelSameFmt()}
"""
Maps ``sys.stderr`` to same logging format for all levels.
"""


class StdStreamFormatMapper(StreamFormatMapper):
    STDERR_ALL_LVL_SAME_FMT: dict[TextIO, LogLevelFmt] = {sys.stderr: StdLogAllLevelSameFmt()}
    """
    Maps ``sys.stderr`` to same logging format for all levels.
    """

    def __init__(self, stream_fmt_map: dict[TextIO, LogLevelFmt] | None = None):
        """
        Maintains a map of the std-log-formatter for each stream.

        :param stream_fmt_map: stream -> ``LogLevelFmt`` map. Defaults to
            ``StdStreamFormatMapper.STDERR_ALL_LVL_SAME_FMT`` when ``None`` or an empty dict is provided.
        """
        self._stream_fmt_map = stream_fmt_map if stream_fmt_map else StdStreamFormatMapper.STDERR_ALL_LVL_SAME_FMT

    @override
    @property
    def stream_fmt_map(self) -> dict[TextIO, LogLevelFmt]:
        return self._stream_fmt_map

    @override
    def fmt_handler(self, stream: TextIO) -> LogLevelFmt:
        return self.stream_fmt_map[stream]
