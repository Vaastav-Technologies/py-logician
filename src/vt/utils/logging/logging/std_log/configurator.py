#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""
import logging
import warnings
from typing import override

from vt.utils.logging.logging import BaseDirectStdAllLevelLogger, BaseDirectAllLevelLogger
from vt.utils.logging.logging.configurators import LoggerConfigurator
from vt.utils.logging.logging.formatters import StreamFormatMapper
from vt.utils.logging.logging.std_log.basic_logger_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.formatters import StdStreamFormatMapper


class DirectStdLoggerConfigurator(LoggerConfigurator):
    DEFAULT_LOG_LEVEL: int = logging.WARNING
    def __init__(self, stream_fmt_mapper: StreamFormatMapper = StdStreamFormatMapper()):
        self.stream_fmt_mapper = stream_fmt_mapper

    @override
    def configure(self, logger: logging.Logger, level: int | str = DEFAULT_LOG_LEVEL) -> BaseDirectStdAllLevelLogger:
        stream_fmt_map = self.stream_fmt_mapper.stream_fmt_map
        BaseDirectAllLevelLogger.register_levels()
        for stream in stream_fmt_map:
            hdlr = logging.StreamHandler(stream=stream) # noqa
            lvl_fmt_handlr = stream_fmt_map[stream]
            try:
                int_level = level if isinstance(level, int) else logging.getLevelNamesMapping()[level]
            except KeyError:
                levels_to_choose_from: list[str] = [logging.getLevelName(level) for level in
                                                    sorted(logging.getLevelNamesMapping().values())]
                prev_formatwarning = warnings.formatwarning
                with warnings.catch_warnings(action="once", category=UserWarning):
                    warnings.formatwarning = lambda message, category, filename, lineno, line=None: f'{category.__name__}: {message}\n'
                    warnings.warn(f"Undefined log level: '{level}'. Choose from {levels_to_choose_from}.")
                    warnings.warn("Setting log level to default: "
                                  f"'{logging.getLevelName(DirectStdLoggerConfigurator.DEFAULT_LOG_LEVEL)}'.")
                warnings.formatwarning = prev_formatwarning
                int_level = DirectStdLoggerConfigurator.DEFAULT_LOG_LEVEL
            hdlr.setFormatter(logging.Formatter(fmt=lvl_fmt_handlr.fmt(int_level)))
            warnings.warn('Checking warning')
            logger.addHandler(hdlr)
            logger.setLevel(int_level)
        return BaseDirectAllLevelLogger(DirectAllLevelLoggerImpl(logger))
