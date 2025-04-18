#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
import os
from typing import override, TextIO, overload, Protocol, Callable

from vt.utils.errors.warnings import vt_warn

from vt.utils.logging.lib_logging import DirectAllLevelLogger, DirectStdAllLevelLogger, VT_ALL_LOG_ENV_VAR
from vt.utils.logging.lib_logging import errmsg_creator
from vt.utils.logging.lib_logging.configurators import LoggerConfigurator, HasUnderlyingConfigurator, \
    LevelLoggerConfigurator
from vt.utils.logging.lib_logging.configurators.vq import V_LITERAL, Q_LITERAL, VQ_DICT_LITERAL, VQConfigurator, \
    VQSepConfigurator, VQCommConfigurator
from vt.utils.logging.lib_logging.configurators.vq.comm import VQCommon
from vt.utils.logging.lib_logging.configurators.vq.sep import VQSepExclusive
from vt.utils.logging.lib_logging.formatters import LogLevelFmt
from vt.utils.logging.lib_logging.std_log import TRACE_LOG_LEVEL, FATAL_LOG_LEVEL, WARNING_LEVEL
from vt.utils.logging.lib_logging.std_log.all_levels_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.lib_logging.std_log.formatters import StdLogAllLevelDiffFmt, \
    StdLogAllLevelSameFmt, STDERR_ALL_LVL_SAME_FMT, STDERR_ALL_LVL_DIFF_FMT
from vt.utils.logging.lib_logging.std_log.utils import get_first_non_none


class StdLoggerConfigurator(LevelLoggerConfigurator[int | str]):
    DEFAULT_LOG_LEVEL_WARNING = WARNING_LEVEL

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
            raise ValueError(errmsg_creator.not_allowed_together('stream_fmt_mapper', 'stream_list'))
        if stream_fmt_mapper is not None and diff_fmt_per_level is not None:
            raise ValueError(errmsg_creator.not_allowed_together('stream_fmt_mapper', 'diff_fmt_per_level'))

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
            if isinstance(level, int):
                int_level = level
            elif level.isdigit():
                int_level = int(level)
            else:
                int_level = logging.getLevelNamesMapping()[level]
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

    @override
    def set_level(self, new_level: int | str) -> int | str:
        orig_level = self.level
        self.level = new_level
        return orig_level


class VQLoggerConfigurator(LoggerConfigurator, VQConfigurator[int | str], HasUnderlyingConfigurator, Protocol):
    """
    Logger configurator that can decorate other configurators to set their underlying logger levels. This log level is
    to be set according to the supplied verbosity and quietness values.
    """
    type T = int | str
    """
    Type for python standard logger logging level.
    """
    VQ_LEVEL_MAP: VQ_DICT_LITERAL[T] = dict(v=logging.INFO, vv=logging.DEBUG, vvv=TRACE_LOG_LEVEL,
                        q=logging.ERROR, qq=logging.CRITICAL, qqq=FATAL_LOG_LEVEL)
    """
    Default {``verbosity-quietness -> logging-level``} mapping.
    """
    DEFAULT_LOG_LEVEL_WARNING: T = WARNING_LEVEL


class VQSepLoggerConfigurator(VQLoggerConfigurator):

    def __init__(self, configurator: LevelLoggerConfigurator[VQLoggerConfigurator.T],
                 verbosity: V_LITERAL | None, quietness: Q_LITERAL | None,
                 vq_level_map: VQ_DICT_LITERAL[VQLoggerConfigurator.T] | None = None,
                 vq_sep_configurator: VQSepConfigurator[VQLoggerConfigurator.T] | None = None,
                 default_log_level: VQLoggerConfigurator.T = VQLoggerConfigurator.DEFAULT_LOG_LEVEL_WARNING):
        """
        A logger configurator that can decorate another logger configurator to accept and infer logging level based on
        ``verbosity`` and ``quietness`` values.

        Default behavior is::

        - verbosity and quietness is to be supplied separately.
        - default_log_level is returned if both are None or not supplied.
        - if both verbosity and quietness are supplied together then a ValueError is raised.

        Last two behaviors can be altered by choosing a different ``vq_sep_configurator``.

        Examples
        ========

        ``verbosity`` and ``quietness`` cannot be supplied together
        -----------------------------------------------------------

        >>> VQSepLoggerConfigurator(StdLoggerConfigurator(), verbosity='v', quietness='qq')
        Traceback (most recent call last):
        ValueError: verbosity and quietness are not allowed together.

        Default ``VQLoggerConfigurator.VQ_LEVEL_MAP`` is used as ``vq_level_map`` when ``vq_level_map`` is ``None``
        -----------------------------------------------------------------------------------------------------------

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), 'v', None)
        >>> assert vq_log.vq_level_map == VQSepLoggerConfigurator.VQ_LEVEL_MAP

        :param configurator: The logger configurator to decorate.
        :param verbosity: verbosity level. Cannot be given with ``quietness``.
        :param quietness: quietness level. Cannot be given with ``verbosity``.
        :param vq_level_map: A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied. Assumes
            ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.
        :param vq_sep_configurator: verbosity quietness configurator. Defaults to ``VQSepExclusive``.
        :param default_log_level: log level when none of the verbosity or quietness is supplied.
        """
        self._vq_level_map = vq_level_map if vq_level_map else VQSepLoggerConfigurator.VQ_LEVEL_MAP
        if vq_sep_configurator:
            self.vq_sep_configurator = vq_sep_configurator
        else:
            self.vq_sep_configurator = VQSepExclusive(self.vq_level_map, warn_only=True)
        self.vq_sep_configurator.validate(verbosity, quietness)
        self.configurator = configurator
        self.verbosity = verbosity
        self.quietness = quietness
        self._underlying_configurator = self.configurator
        self.default_log_level = default_log_level

    @override
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        int_level = self.vq_sep_configurator.get_effective_level(self.verbosity, self.quietness, self.default_log_level)
        ret_logger = self.configurator.configure(logger)
        ret_logger.underlying_logger.setLevel(int_level)
        return ret_logger

    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[VQLoggerConfigurator.T]:
        return self._vq_level_map

    @property
    def underlying_configurator(self) -> LoggerConfigurator:
        return self._underlying_configurator


class VQCommLoggerConfigurator(VQLoggerConfigurator, LevelLoggerConfigurator[V_LITERAL | Q_LITERAL | None]):

    def __init__(self, ver_qui: V_LITERAL | Q_LITERAL | None,
                 configurator: LevelLoggerConfigurator[VQLoggerConfigurator.T],
                 vq_level_map: VQ_DICT_LITERAL[VQLoggerConfigurator.T] | None = None,
                 vq_comm_configurator: VQCommConfigurator[VQLoggerConfigurator.T] | None = None,
                 default_log_level: VQLoggerConfigurator.T = VQLoggerConfigurator.DEFAULT_LOG_LEVEL_WARNING):
        """
        A logger configurator that can decorate another logger configurator to accept and infer logging level based on
        ``verbosity`` or ``quietness`` values.

        Default behavior is::

        - verbosity or quietness is to be supplied in one inclusive argument.
        - default_log_level is returned if both are None or not supplied.

        Last behavior can be altered by choosing a different ``vq_comm_configurator``.

        Examples
        ========

        ``verbosity`` or ``quietness`` to be supplied as one argument.
        --------------------------------------------------------------

        >>> _ = VQCommLoggerConfigurator('qq', StdLoggerConfigurator())

        Default ``VQLoggerConfigurator.VQ_LEVEL_MAP`` is used as ``vq_level_map`` when ``vq_level_map`` is ``None``
        -----------------------------------------------------------------------------------------------------------

        >>> vq_log = VQCommLoggerConfigurator('v', StdLoggerConfigurator())
        >>> assert vq_log.vq_level_map == VQSepLoggerConfigurator.VQ_LEVEL_MAP

        :param configurator: The logger configurator to decorate.
        :param ver_qui: verbosity or quietness level.
        :param vq_level_map: A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied. Assumes
            ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.
        :param vq_comm_configurator: verbosity quietness configurator. Defaults to ``VQCommon``.
        :param default_log_level: log level when none of the verbosity or quietness is supplied.
        """
        self._vq_level_map = vq_level_map if vq_level_map else VQCommLoggerConfigurator.VQ_LEVEL_MAP
        if vq_comm_configurator:
            self.vq_comm_configurator = vq_comm_configurator
        else:
            self.vq_comm_configurator = VQCommon(self.vq_level_map, warn_only=True)
        self.vq_comm_configurator.validate(ver_qui)
        self.configurator = configurator
        self.ver_qui = ver_qui
        self._underlying_configurator = self.configurator
        self.default_log_level = default_log_level

    @override
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        int_level = self.vq_comm_configurator.get_effective_level(self.ver_qui, self.default_log_level)
        self.configurator.set_level(int_level)
        return self.configurator.configure(logger)

    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[VQLoggerConfigurator.T]:
        return self._vq_level_map

    @property
    def underlying_configurator(self) -> LevelLoggerConfigurator[VQLoggerConfigurator.T]:
        return self._underlying_configurator

    @override
    def set_level(self, new_ver_qui: V_LITERAL | Q_LITERAL | None) -> V_LITERAL | Q_LITERAL | None:
        orig_ver_qui = self.ver_qui
        self.ver_qui = new_ver_qui
        return orig_ver_qui


class SupplierLoggerConfigurator[T](LoggerConfigurator):
    def __init__(self, level_supplier: Callable[[], T], configurator: LevelLoggerConfigurator[T]):
        self.level_supplier = level_supplier
        self.configurator = configurator

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        final_level = self.level_supplier()
        self.configurator.set_level(final_level)
        return self.configurator.configure(logger)


class ListLoggerConfigurator[T](LoggerConfigurator):

    def __init__(self, level_list: list[T], configurator: LevelLoggerConfigurator,
                 level_pickup_strategy =get_first_non_none):
        if not level_list:
            raise ValueError("Level list must not be None or empty.")
        self.level_list = level_list
        self.configurator = configurator
        self.level_pickup_strategy = level_pickup_strategy

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        final_level = self.level_pickup_strategy(self.level_list)
        if final_level:
            self.configurator.set_level(final_level)
        return self.configurator.configure(logger)


class EnvListLC[T](ListLoggerConfigurator):
    def __init__(self, env_list: list[str], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy =get_first_non_none):
        super().__init__([os.getenv(e) for e in env_list], configurator, level_pickup_strategy)
        self._env_list = env_list

    def get_env_list(self):
        return self._env_list


class VTEnvListLC[T](EnvListLC[T]):
    def __init__(self, env_list: list[str], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy=get_first_non_none):
        env_list.append(VT_ALL_LOG_ENV_VAR)
        super().__init__(env_list, configurator, level_pickup_strategy)
