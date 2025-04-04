#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
import warnings
from typing import override

from vt.utils.logging.logging import BaseDirectStdAllLevelLogger, DirectAllLevelLogger
from vt.utils.logging.logging.configurators import LoggerConfigurator
from vt.utils.logging.logging.formatters import StreamFormatMapper
from vt.utils.logging.logging.std_log.basic_logger_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.formatters import StdStreamFormatMapper
from vt.utils.logging.warnings import suppress_warning_stacktrace


class DirectStdLoggerConfigurator(LoggerConfigurator):
    WARNING_LOG_LEVEL: int = logging.WARNING

    def __init__(self, stream_fmt_mapper: StreamFormatMapper = StdStreamFormatMapper()):
        """
        Perform logger configuration using the python's std logger calls.

        :param stream_fmt_mapper: an output-stream -> log format mapper.
        """
        self.stream_fmt_mapper = stream_fmt_mapper

    @override
    def configure(self, logger: logging.Logger, level: int | str = WARNING_LOG_LEVEL) -> BaseDirectStdAllLevelLogger:
        stream_fmt_map = self.stream_fmt_mapper.stream_fmt_map
        DirectAllLevelLogger.register_levels()
        for stream in stream_fmt_map:
            hdlr = logging.StreamHandler(stream=stream) # noqa
            lvl_fmt_handlr = stream_fmt_map[stream]
            try:
                int_level = level if isinstance(level, int) else logging.getLevelNamesMapping()[level]
            except KeyError:
                levels_to_choose_from: list[str] = [logging.getLevelName(level) for level in
                                                    sorted(logging.getLevelNamesMapping().values())]
                with suppress_warning_stacktrace():
                    warnings.warn(f"{logger.name}: Undefined log level '{level}'. "
                                  f"Choose from {levels_to_choose_from}.")
                    warnings.warn(f"{logger.name}: Setting log level to default: "
                                  f"'{logging.getLevelName(DirectStdLoggerConfigurator.WARNING_LOG_LEVEL)}'.")
                int_level = DirectStdLoggerConfigurator.WARNING_LOG_LEVEL
            hdlr.setFormatter(logging.Formatter(fmt=lvl_fmt_handlr.fmt(int_level)))
            logger.addHandler(hdlr)
            logger.setLevel(int_level)
        return DirectAllLevelLogger(DirectAllLevelLoggerImpl(logger))
