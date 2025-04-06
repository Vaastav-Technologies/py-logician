#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
import sys
import warnings
from typing import override

from vt.utils.logging.logging import DirectAllLevelLogger
from vt.utils.logging.logging.configurators import LoggerConfigurator
from vt.utils.logging.logging.formatters import StreamFormatMapper
from vt.utils.logging.logging.std_log.all_levels_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.formatters import StdStreamFormatMapper
from vt.utils.logging.logging.std_log.utils import level_name_mapping
from vt.utils.logging.warnings import suppress_warning_stacktrace


class StdLoggerConfigurator(LoggerConfigurator):
    WARNING_LOG_LEVEL: int = logging.WARNING

    def __init__(self, *, level: int | str = WARNING_LOG_LEVEL, cmd_name: str | None = None,
                 stream_fmt_mapper: StreamFormatMapper = StdStreamFormatMapper(),
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        """
        Perform logger configuration using the python's std logger calls.

        :param level: active logging level.
        :param cmd_name: The command name to register the command logging level to. If `None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.
        :param stream_fmt_mapper: an output-stream -> log format mapper.
        :param level_name_map: log level - name mapping. This mapping updates the std python logging library's
            registered log levels . Check ``DirectAllLevelLogger.register_levels()`` for more info.
        :param no_warn: do not warn if a supplied level is not registered with the logging library.
        """
        self.level = level
        self.cmd_name = cmd_name
        self.stream_fmt_mapper = stream_fmt_mapper
        self.level_name_map = level_name_map
        self.no_warn = no_warn

    @override
    def configure(self, logger: logging.Logger) -> DirectAllLevelLogger:
        stream_fmt_map = self.stream_fmt_mapper.stream_fmt_map
        level = self.level
        cmd_name = self.cmd_name
        DirectAllLevelLogger.register_levels(self.level_name_map)
        for stream in stream_fmt_map:
            hdlr = logging.StreamHandler(stream=stream) # noqa
            lvl_fmt_handlr = stream_fmt_map[stream]
            try:
                int_level = level if isinstance(level, int) else logging.getLevelNamesMapping()[level]
            except KeyError:
                if not self.no_warn:
                    levels_to_choose_from: dict[int, str] = level_name_mapping()
                    with suppress_warning_stacktrace():
                        warnings.warn(f"{logger.name}: Undefined log level '{level}'. "
                                      f"Choose from {list(levels_to_choose_from.values())}.")
                        warnings.warn(f"{logger.name}: Setting log level to default: "
                                      f"'{logging.getLevelName(StdLoggerConfigurator.WARNING_LOG_LEVEL)}'.")
                int_level = StdLoggerConfigurator.WARNING_LOG_LEVEL
            hdlr.setFormatter(logging.Formatter(fmt=lvl_fmt_handlr.fmt(int_level)))
            logger.addHandler(hdlr)
            logger.setLevel(int_level)
        return DirectAllLevelLogger(DirectAllLevelLoggerImpl(logger), cmd_name=cmd_name)
