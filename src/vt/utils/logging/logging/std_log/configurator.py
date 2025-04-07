#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
import sys
import warnings
from typing import override, TextIO, overload

from vt.utils.logging.logging import DirectAllLevelLogger
from vt.utils.logging.logging.configurators import LoggerConfigurator
from vt.utils.logging.logging.formatters import LogLevelFmt
from vt.utils.logging.logging.std_log.all_levels_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.formatters import StdLogAllLevelDiffFmt, \
    StdLogAllLevelSameFmt
from vt.utils.logging.logging.std_log.utils import level_name_mapping
from vt.utils.logging.warnings import suppress_warning_stacktrace


class StdLoggerConfigurator(LoggerConfigurator):
    WARNING_LOG_LEVEL: int = logging.WARNING

    @overload
    def __init__(self, *, level: int | str = WARNING_LOG_LEVEL, cmd_name: str | None = None,
                 diff_fmt_per_level: bool | None = None, stream_list: list[TextIO] | None = None,
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        ...

    @overload
    def __init__(self, *, level: int | str = WARNING_LOG_LEVEL, cmd_name: str | None = None,
                 stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None = None,
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        ...

    def __init__(self, *, level: int | str = WARNING_LOG_LEVEL, cmd_name: str | None = None,
                 stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None = None,
                 diff_fmt_per_level: bool | None = None, stream_list: list[TextIO] | None = None,
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        """
        Perform logger configuration using the python's std logger calls.

        :param level: active logging level.
        :param cmd_name: The command name to register the command logging level to. If `None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.
        :param stream_fmt_mapper: an output-stream -> log format mapper. Cannot be used with ``diff_fmt_per_level``
            and ``stream_list``.
        :param diff_fmt_per_level: Use different log format per logging level. Cannot be provided with
            ``stream_fmt_mapper``.
        :param stream_list: list of streams to apply level formatting logic to. Cannot be provided with
            ``stream_fmt_mapper``.
        :param level_name_map: log level - name mapping. This mapping updates the std python logging library's
            registered log levels . Check ``DirectAllLevelLogger.register_levels()`` for more info.
        :param no_warn: do not warn if a supplied level is not registered with the logging library.
        """
        if stream_fmt_mapper is not None and stream_list is not None:
            raise ValueError("Cannot provide both 'stream_fmt_mapper' and 'stream_list'. Choose one.")
        if stream_fmt_mapper is not None and diff_fmt_per_level is not None:
            raise ValueError("Cannot provide both 'stream_fmt_mapper' and 'diff_fmt_per_level'. Choose one.")

        self.level = level
        self.cmd_name = cmd_name
        self.level_name_map = level_name_map
        self.no_warn = no_warn
        if stream_fmt_mapper:
            self.stream_list = list(stream_fmt_mapper.keys())
            self.stream_fmt_mapper = stream_fmt_mapper
        else:
            self.stream_fmt_mapper = dict()
            self.stream_list = stream_list if stream_list else [sys.stderr]
            if diff_fmt_per_level:
                self.stream_fmt_mapper = {_stream: StdLogAllLevelDiffFmt() for _stream in self.stream_list}
            else:
                self.stream_fmt_mapper = {_stream: StdLogAllLevelSameFmt() for _stream in self.stream_list}

    @override
    def configure(self, logger: logging.Logger) -> DirectAllLevelLogger:
        stream_fmt_map = self.stream_fmt_mapper
        level = self.level
        levels_to_choose_from: dict[int, str] = DirectAllLevelLogger.register_levels(self.level_name_map)
        try:
            int_level = level if isinstance(level, int) else logging.getLevelNamesMapping()[level]
        except KeyError:
            if not self.no_warn:
                with suppress_warning_stacktrace():
                    warnings.warn(f"{logger.name}: Undefined log level '{level}'. "
                                  f"Choose from {list(levels_to_choose_from.values())}.")
                    warnings.warn(f"{logger.name}: Setting log level to default: "
                                  f"'{logging.getLevelName(StdLoggerConfigurator.WARNING_LOG_LEVEL)}'.")
            int_level = StdLoggerConfigurator.WARNING_LOG_LEVEL
        logger.setLevel(int_level)
        for stream in stream_fmt_map:
            hdlr = logging.StreamHandler(stream=stream) # noqa
            lvl_fmt_handlr = stream_fmt_map[stream]
            hdlr.setFormatter(logging.Formatter(fmt=lvl_fmt_handlr.fmt(int_level)))
            logger.addHandler(hdlr)
        return DirectAllLevelLogger(DirectAllLevelLoggerImpl(logger), cmd_name=self.cmd_name)
