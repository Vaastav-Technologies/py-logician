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
    DEFAULT_LOGGER_FMT = TIMED_DETAIL_LOG_FMT

    def __init__(self, fmt: str = DEFAULT_LOGGER_FMT):
        self._fmt = fmt

    @override
    def fmt(self, level: int | str) -> str:
        return self._fmt


class StdLogAllLevelDiffFmt(DiffLevelDiffFmt):
    DEFAULT_LOGGER_DICT: dict[int | str, str] = {
        TRACE_LOG_LEVEL: TIMED_DETAIL_LOG_FMT,
        logging.DEBUG: DETAIL_LOG_FMT,
        logging.INFO: SHORT_LOG_FMT,
        logging.WARN: SHORTER_LOG_FMT
    }

    def __init__(self, fmt_dict: dict[int | str, str] | None = None):
        self._fmt_dict = fmt_dict if fmt_dict else StdLogAllLevelDiffFmt.DEFAULT_LOGGER_DICT

    @override
    def fmt(self, level: int | str) -> str:
        final_level = level if level in self._fmt_dict else self.next_approx_level(level)
        return self._fmt_dict[final_level]

    def next_approx_level(self, missing_level: int | str) -> int | str:
        pass


class StdStreamFormatMapper(StreamFormatMapper):
    DEFAULT_STREAM_FMT_DICT: dict[TextIO, LogLevelFmt] = {sys.stderr: StdLogAllLevelSameFmt()}

    def __init__(self, stream_fmt_map: dict[TextIO, LogLevelFmt] | None = None):
        self._stream_fmt_map = stream_fmt_map if stream_fmt_map else StdStreamFormatMapper.DEFAULT_STREAM_FMT_DICT

    @override
    @property
    def stream_fmt_map(self) -> dict[TextIO, LogLevelFmt]:
        return self._stream_fmt_map

    @override
    def fmt_handler(self, stream: TextIO) -> LogLevelFmt:
        return self.stream_fmt_map[stream]
