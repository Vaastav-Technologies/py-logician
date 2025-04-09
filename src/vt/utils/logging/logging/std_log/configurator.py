#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
import warnings
from typing import override, TextIO, overload, Literal

from vt.utils.logging.logging import DirectAllLevelLogger, DirectStdAllLevelLogger
from vt.utils.logging.logging.configurators import LoggerConfigurator, VQConfigurator, VQ_DICT_LITERAL, V_LITERAL, \
    Q_LITERAL
from vt.utils.logging.logging.formatters import LogLevelFmt
from vt.utils.logging.logging.std_log import TRACE_LOG_LEVEL, FATAL_LOG_LEVEL
from vt.utils.logging.logging.std_log.all_levels_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.formatters import StdLogAllLevelDiffFmt, \
    StdLogAllLevelSameFmt, STDERR_ALL_LVL_SAME_FMT, STDERR_ALL_LVL_DIFF_FMT
from vt.utils.logging.warnings import vt_warn


class StdLoggerConfigurator(LoggerConfigurator):
    DEFAULT_LOG_LEVEL_WARNING: int = logging.WARNING

    @overload
    def __init__(self, *, level: int | str = DEFAULT_LOG_LEVEL_WARNING, cmd_name: str | None = None,
                 diff_fmt_per_level: bool | None = None, stream_list: list[TextIO] | None = None,
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        ...

    @overload
    def __init__(self, *, level: int | str = DEFAULT_LOG_LEVEL_WARNING, cmd_name: str | None = None,
                 stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None = None,
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        ...

    def __init__(self, *, level: int | str = DEFAULT_LOG_LEVEL_WARNING, cmd_name: str | None = None,
                 stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None = None,
                 diff_fmt_per_level: bool | None = None, stream_list: list[TextIO] | None = None,
                 level_name_map: dict[int, str] | None = None, no_warn: bool = False):
        """
        Perform logger configuration using the python's std logger calls.

        :param level: active logging level.
        :param cmd_name: The command name to register the command logging level to. If ``None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.
        :param stream_fmt_mapper: an output-stream -> log format mapper. Defaults to ``STDERR_ALL_LVL_SAME_FMT`` if
            ``None`` is supplied. Cannot be used with ``diff_fmt_per_level``
            and ``stream_list``. Note that ``{}`` denoting an empty stream_fmt_mapper is accepted and specifies
            the user's intent of not logging to any stream.
        :param diff_fmt_per_level: Use different log format per logging level. Cannot be provided with
            ``stream_fmt_mapper``.
        :param stream_list: list of streams to apply level formatting logic to. Cannot be provided with
            ``stream_fmt_mapper``.Note that ``[]`` denoting an empty stream_list is accepted and specifies
            the user's intent of not logging to any stream.
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
        if stream_fmt_mapper is not None: # accepts empty stream_fmt_mapper
            self.stream_fmt_mapper = stream_fmt_mapper
        else:
            if stream_list is not None: # accepts empty stream_list
                if diff_fmt_per_level:
                    self.stream_fmt_mapper = {stream: StdLogAllLevelDiffFmt() for stream in stream_list}
                else:
                    self.stream_fmt_mapper = {stream: StdLogAllLevelSameFmt() for stream in stream_list}
            else:
                if diff_fmt_per_level:
                    self.stream_fmt_mapper = STDERR_ALL_LVL_DIFF_FMT
                else:
                    self.stream_fmt_mapper = STDERR_ALL_LVL_SAME_FMT

    @override
    def configure(self, logger: logging.Logger) -> DirectAllLevelLogger:
        stream_fmt_map = self.stream_fmt_mapper
        level = self.level
        levels_to_choose_from: dict[int, str] = DirectAllLevelLogger.register_levels(self.level_name_map)
        try:
            int_level = level if isinstance(level, int) else logging.getLevelNamesMapping()[level]
        except KeyError:
            if not self.no_warn:
                vt_warn(f"{logger.name}: Undefined log level '{level}'. "
                              f"Choose from {list(levels_to_choose_from.values())}.")
                vt_warn(f"{logger.name}: Setting log level to default: "
                              f"'{logging.getLevelName(StdLoggerConfigurator.DEFAULT_LOG_LEVEL_WARNING)}'.")
            int_level = StdLoggerConfigurator.DEFAULT_LOG_LEVEL_WARNING
        logger.setLevel(int_level)
        if not stream_fmt_map:  # empty map
            for handler in logger.handlers:
                logger.removeHandler(handler)
            logger.addHandler(logging.NullHandler())
        else:
            for stream in stream_fmt_map:
                hdlr = logging.StreamHandler(stream=stream) # noqa
                lvl_fmt_handlr = stream_fmt_map[stream]
                hdlr.setFormatter(logging.Formatter(fmt=lvl_fmt_handlr.fmt(int_level)))
                logger.addHandler(hdlr)
        return DirectAllLevelLogger(DirectAllLevelLoggerImpl(logger), cmd_name=self.cmd_name)


class VQLoggerConfigurator(LoggerConfigurator):
    VQ_LEVEL_MAP: VQ_DICT_LITERAL[int] = dict(v=logging.INFO, vv=logging.DEBUG, vvv=TRACE_LOG_LEVEL,
                        q=logging.ERROR, qq=logging.CRITICAL, qqq=FATAL_LOG_LEVEL)
    """
    Default {``verbosity-quietness -> logging-level``} mapping.
    """

    def __init__(self, configurator: LoggerConfigurator, *,
                 verbosity: V_LITERAL | None = None,
                 quietness: Q_LITERAL | None = None,
                 vq_level_map: VQ_DICT_LITERAL[int] | None = None):
        """
        A logger configurator that can decorate another logger configurator to accept and infer logging level based on
        ``verbosity`` and ``quietness`` values.

        Examples
        ========

        ``verbosity`` and ``quietness`` cannot be supplied together
        -----------------------------------------------------------

        >>> VQLoggerConfigurator(StdLoggerConfigurator(), verbosity='v', quietness='qq')
        Traceback (most recent call last):
        ValueError: 'verbosity' and 'quietness' cannot be given together.

        Default ``VQLoggerConfigurator.VQ_LEVEL_MAP`` is used as ``vq_level_map`` when ``vq_level_map`` is ``None``
        -----------------------------------------------------------------------------------------------------------

        >>> vq_log = VQLoggerConfigurator(StdLoggerConfigurator())
        >>> assert vq_log.vq_level_map == VQLoggerConfigurator.VQ_LEVEL_MAP

        :param configurator: The logger configurator to decorate.
        :param verbosity: verbosity level. Cannot be given with ``quietness``.
        :param quietness: quietness level. Cannot be given with ``verbosity``.
        :param vq_level_map: A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied. Assumes
            ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.
        """
        if verbosity and quietness:
            raise ValueError("'verbosity' and 'quietness' cannot be given together.")
        self.configurator = configurator
        self.vq_level_map = vq_level_map if vq_level_map else VQLoggerConfigurator.VQ_LEVEL_MAP
        self.verbosity = verbosity
        self.quietness = quietness

    @override
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        if self.verbosity:
            int_level = self.vq_level_map[self.verbosity]
        elif self.quietness:
            int_level = self.vq_level_map[self.quietness]
        else:
            int_level = logging.WARNING
        ret_logger = self.configurator.configure(logger)
        ret_logger.underlying_logger.setLevel(int_level)
        return ret_logger
