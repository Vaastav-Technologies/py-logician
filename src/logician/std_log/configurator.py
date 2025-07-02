#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
from typing import override, TextIO, overload, Protocol

from vt.utils.errors.warnings import vt_warn

from logician import DirectAllLevelLogger, DirectStdAllLevelLogger
from logician import errmsg_creator
from logician.configurators import LoggerConfigurator, HasUnderlyingConfigurator, \
    LevelLoggerConfigurator
from logician.configurators.vq import V_LITERAL, Q_LITERAL, VQ_DICT_LITERAL, VQConfigurator, \
    VQSepConfigurator, VQCommConfigurator
from logician.configurators.vq.comm import VQCommon
from logician.configurators.vq.sep import VQSepExclusive
from logician.formatters import LogLevelFmt
from logician.std_log import TRACE_LOG_LEVEL, FATAL_LOG_LEVEL, WARNING_LEVEL
from logician.std_log.all_levels_impl import DirectAllLevelLoggerImpl
from logician.std_log.formatters import StdLogAllLevelDiffFmt, \
    StdLogAllLevelSameFmt, STDERR_ALL_LVL_SAME_FMT, STDERR_ALL_LVL_DIFF_FMT


class StdLoggerConfigurator(LevelLoggerConfigurator[int | str]):

    LOG_LEVEL_WARNING = WARNING_LEVEL
    CMD_NAME_NONE = None
    STREAM_FMT_MAPPER_NONE = None
    FMT_PER_LEVEL_NONE = None
    STREAM_LIST_NONE = None
    LEVEL_NAME_MAP_NONE = None
    NO_WARN_FALSE = False

    @overload
    def __init__(self, *, level: int | str = LOG_LEVEL_WARNING, cmd_name: str | None = CMD_NAME_NONE,
                 same_fmt_per_level: bool | None = FMT_PER_LEVEL_NONE,
                 stream_list: list[TextIO] | None = STREAM_LIST_NONE,
                 level_name_map: dict[int, str] | None = LEVEL_NAME_MAP_NONE, no_warn: bool = NO_WARN_FALSE):
        ...

    @overload
    def __init__(self, *, level: int | str = LOG_LEVEL_WARNING, cmd_name: str | None = CMD_NAME_NONE,
                 stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None = STREAM_FMT_MAPPER_NONE,
                 level_name_map: dict[int, str] | None = LEVEL_NAME_MAP_NONE, no_warn: bool = NO_WARN_FALSE):
        ...

    def __init__(self, *, level: int | str = LOG_LEVEL_WARNING, cmd_name: str | None = CMD_NAME_NONE,
                 stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None = STREAM_FMT_MAPPER_NONE,
                 same_fmt_per_level: bool | None = FMT_PER_LEVEL_NONE,
                 stream_list: list[TextIO] | None = STREAM_LIST_NONE,
                 level_name_map: dict[int, str] | None = LEVEL_NAME_MAP_NONE, no_warn: bool = NO_WARN_FALSE):
        """
        Perform logger configuration using the python's std logger calls.

        :param level: active logging level.
        :param cmd_name: The command name to register the command logging level to. If ``None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.
        :param stream_fmt_mapper: an output-stream -> log format mapper. Defaults to ``STDERR_ALL_LVL_DIFF_FMT`` if
            ``None`` is supplied. Cannot be used with ``same_fmt_per_level``
            and ``stream_list``. Note that ``{}`` denoting an empty ``stream_fmt_mapper`` is accepted and specifies
            the user's intent of not logging to any stream.
        :param same_fmt_per_level: Use same log format per logging level. Cannot be provided with
            ``stream_fmt_mapper``.
        :param stream_list: list of streams to apply level formatting logic to. Cannot be provided with
            ``stream_fmt_mapper``. Note that ``[]`` denoting an empty stream_list is accepted and specifies
            the user's intent of not logging to any stream.
        :param level_name_map: log level - name mapping. This mapping updates the std python logging library's
            registered log levels . Check ``DirectAllLevelLogger.register_levels()`` for more info.
        :param no_warn: do not warn if a supplied level is not registered with the logging library.
        """
        self.validate_args(stream_fmt_mapper, stream_list, same_fmt_per_level)

        self._level = level
        self.cmd_name = cmd_name
        self.level_name_map = level_name_map
        self.no_warn = no_warn
        if stream_fmt_mapper is not None: # accepts empty stream_fmt_mapper
            self.stream_fmt_mapper = stream_fmt_mapper
        else:
            self.stream_fmt_mapper = self.compute_stream_fmt_mapper(same_fmt_per_level, stream_list)

    @staticmethod
    def compute_stream_fmt_mapper(same_fmt_per_level: bool | None,
                                  stream_list: list[TextIO] | None) -> dict[TextIO, LogLevelFmt]:
        """
        Compute the stream format mapper form supplied arguments.

        :param same_fmt_per_level: Want same format per logging level?
        :param stream_list: List of streams this format configuration is to be applied to. Note that ``[]`` denoting an
            empty stream_list is accepted and specifies the user's intent of not logging to any stream.
        :return: a configured ``stream_fmt_mapper``.
        """
        if stream_list is not None:  # accepts empty stream_list
            if same_fmt_per_level:
                return {stream: StdLogAllLevelSameFmt() for stream in stream_list}
            return {stream: StdLogAllLevelDiffFmt() for stream in stream_list}
        else:
            if same_fmt_per_level:
                return STDERR_ALL_LVL_SAME_FMT
            return STDERR_ALL_LVL_DIFF_FMT

    @override
    def configure(self, logger: logging.Logger) -> DirectAllLevelLogger:
        """
        Configure the std python logger for various formatting quick-hands.

        Examples:

        * Configure with defaults, no errors::

            >>> logger_defaults = StdLoggerConfigurator().configure(logging.getLogger('logger-defaults'))

        * Set ``int`` level::

            >>> logger_int = StdLoggerConfigurator(level=20).configure(logging.getLogger('logger-int'))
            >>> assert logger_int.underlying_logger.level == 20

        * Set digit ``str`` level::

            >>> logger_int_str = StdLoggerConfigurator(level='20').configure(logging.getLogger('logger-int-str'))
            >>> assert logger_int_str.underlying_logger.level == 20

        * Set ``str`` level::

            >>> logger_str = StdLoggerConfigurator(level='FATAL').configure(logging.getLogger('logger-str'))
            >>> assert logger_str.underlying_logger.level == FATAL_LOG_LEVEL

        * ``None`` level sets default `WARNING` log level::

            >>> logger_none = (StdLoggerConfigurator(level=None) # noqa
            ...     .configure(logging.getLogger('logger-none')))
            >>> assert logger_none.underlying_logger.level == StdLoggerConfigurator.LOG_LEVEL_WARNING

        * Any other level type raises a ``TypeError``:

          * ``dict`` example:

            >>> logger_dict = (StdLoggerConfigurator(level={}) # noqa
            ...     .configure(logging.getLogger('logger-dict')))
            Traceback (most recent call last):
            TypeError: Wrong level value supplied: '{}', Expected int or str, got dict

          * ``list`` example:

            >>> logger_list = (StdLoggerConfigurator(level=[]) # noqa
            ...     .configure(logging.getLogger('logger-list')))
            Traceback (most recent call last):
            TypeError: Wrong level value supplied: '[]', Expected int or str, got list


        :param logger: std python logger.
        :return: A configured All level logging std python logger.
        """
        stream_fmt_map = self.stream_fmt_mapper
        level = self.level
        levels_to_choose_from: dict[int, str] = DirectAllLevelLogger.register_levels(self.level_name_map)
        try:
            match level:
                case int():
                    int_level = level
                case str():
                    int_level = int(level) if level.isdigit() else logging.getLevelNamesMapping()[level]
                case None:
                    int_level = StdLoggerConfigurator.LOG_LEVEL_WARNING
                case _:
                    raise TypeError(f"Wrong level value supplied: '{level}', Expected int or str, got "
                                    f"{type(level).__name__}")
        except KeyError:
            if not self.no_warn:
                vt_warn(f"{logger.name}: Undefined log level '{level}'. "
                              f"Choose from {list(levels_to_choose_from.values())}.")
                vt_warn(f"{logger.name}: Setting log level to default: "
                              f"'{logging.getLevelName(StdLoggerConfigurator.LOG_LEVEL_WARNING)}'.")
            int_level = StdLoggerConfigurator.LOG_LEVEL_WARNING
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
        self._level = new_level
        return orig_level

    @override
    @property
    def level(self) -> int | str:
        return self._level

    @override
    def clone_with(self, **kwargs) -> 'StdLoggerConfigurator':
        """
        kwargs:
            ``level`` - active logging level.

            ``cmd_name`` - The command name to register the command logging level to. If ``None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.

            ``stream_fmt_mapper`` - an output-stream -> log format mapper. Defaults to ``STDERR_ALL_LVL_DIFF_FMT`` if
            ``None`` is supplied. Cannot be used with ``same_fmt_per_level``
            and ``stream_list``. Note that ``{}`` denoting an empty ``stream_fmt_mapper`` is accepted and specifies
            the user's intent of not logging to any stream.

            ``diff_fmt_per_level`` - Use different log format per logging level. Cannot be provided with
            ``stream_fmt_mapper``.

            ``stream_list`` - list of streams to apply level formatting logic to. Cannot be provided with
            ``stream_fmt_mapper``.Note that ``[]`` denoting an empty stream_list is accepted and specifies the user's
            intent of not logging to any stream.

            ``level_name_map`` - log level - name mapping. This mapping updates the std python logging library's
            registered log levels . Check ``DirectAllLevelLogger.register_levels()`` for more info.

            ``no_warn`` - do not warn if a supplied level is not registered with the logging library.
        :return: new ``StdLoggerConfigurator``.
        """
        level = kwargs.pop('level', self.level)
        cmd_name = kwargs.pop('cmd_name', self.cmd_name)
        diff_fmt_per_level = kwargs.pop('diff_fmt_per_level', StdLoggerConfigurator.FMT_PER_LEVEL_NONE)
        stream_list = kwargs.pop('stream_list', StdLoggerConfigurator.STREAM_LIST_NONE)
        stream_fmt_mapper = kwargs.pop('stream_fmt_mapper', None)
        self.validate_args(stream_fmt_mapper, stream_list, diff_fmt_per_level)
        stream_fmt_mapper = stream_fmt_mapper if stream_fmt_mapper is not None else self.stream_fmt_mapper
        level_name_map = kwargs.pop('level_name_map', self.level_name_map)
        no_warn = kwargs.pop('no_warn', self.no_warn)
        if stream_fmt_mapper is not None:
            return StdLoggerConfigurator(level=level, cmd_name=cmd_name, stream_fmt_mapper=stream_fmt_mapper,
                     level_name_map=level_name_map, no_warn=no_warn)
        else:
            return StdLoggerConfigurator(level=level, cmd_name=cmd_name, stream_list=stream_list,
                                         same_fmt_per_level=diff_fmt_per_level, level_name_map=level_name_map,
                                         no_warn=no_warn)

    @staticmethod
    def validate_args(stream_fmt_mapper: dict[TextIO, LogLevelFmt] | None, stream_list: list[TextIO] | None,
                      diff_fmt_per_level: bool | None):
        """
        :raises ValueError: if  ``stream_fmt_mapper`` is given with ``stream_list`` or
            if  ``stream_fmt_mapper`` is given with ``diff_fmt_per_level``.
        """
        if stream_fmt_mapper is not None and stream_list is not None:
            raise ValueError(errmsg_creator.not_allowed_together('stream_fmt_mapper', 'stream_list'))
        if stream_fmt_mapper is not None and diff_fmt_per_level is not None:
            raise ValueError(errmsg_creator.not_allowed_together('stream_fmt_mapper', 'diff_fmt_per_level'))


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
    LOG_LEVEL_WARNING: T = WARNING_LEVEL


class VQSepLoggerConfigurator(VQLoggerConfigurator):

    VQ_LEVEL_MAP_NONE = None
    VQ_SEP_CONF_NONE = None
    LOG_LEVEL_WARNING = VQLoggerConfigurator.LOG_LEVEL_WARNING

    @overload
    def __init__(self, configurator: LevelLoggerConfigurator[VQLoggerConfigurator.T],
                 verbosity: int | None, quietness: int | None,
                 vq_level_map: VQ_DICT_LITERAL[VQLoggerConfigurator.T] | None = VQ_LEVEL_MAP_NONE,
                 vq_sep_configurator: VQSepConfigurator[VQLoggerConfigurator.T] | None = VQ_SEP_CONF_NONE,
                 default_log_level: VQLoggerConfigurator.T = LOG_LEVEL_WARNING):
        ...

    @overload
    def __init__(self, configurator: LevelLoggerConfigurator[VQLoggerConfigurator.T],
                 verbosity: V_LITERAL | None, quietness: Q_LITERAL | None,
                 vq_level_map: VQ_DICT_LITERAL[VQLoggerConfigurator.T] | None = VQ_LEVEL_MAP_NONE,
                 vq_sep_configurator: VQSepConfigurator[VQLoggerConfigurator.T] | None = VQ_SEP_CONF_NONE,
                 default_log_level: VQLoggerConfigurator.T = LOG_LEVEL_WARNING):
        ...

    def __init__(self, configurator: LevelLoggerConfigurator[VQLoggerConfigurator.T],
                 verbosity: V_LITERAL | int | None, quietness: Q_LITERAL | int | None,
                 vq_level_map: VQ_DICT_LITERAL[VQLoggerConfigurator.T] | None = VQ_LEVEL_MAP_NONE,
                 vq_sep_configurator: VQSepConfigurator[VQLoggerConfigurator.T] | None = VQ_SEP_CONF_NONE,
                 default_log_level: VQLoggerConfigurator.T = LOG_LEVEL_WARNING):
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

        >>> import warnings

        ``verbosity`` and ``quietness`` cannot be supplied together
        -----------------------------------------------------------
        Warning is issued.
        >>> with warnings.catch_warnings(record=True) as w:
        ...     vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), verbosity='v', quietness='qq')
        ...     assert "verbosity and quietness are not allowed together" in str(w.pop().message)
        >>> assert vq_log.configurator.level == vq_log.default_log_level

        Default ``VQLoggerConfigurator.VQ_LEVEL_MAP`` is used as ``vq_level_map`` when ``vq_level_map`` is ``None``
        -----------------------------------------------------------------------------------------------------------

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), 'v', None)
        >>> assert vq_log.vq_level_map == VQSepLoggerConfigurator.VQ_LEVEL_MAP

        ``int`` can be supplied for verbosity value
        ------------------------------------------

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), 2, None)
        >>> assert vq_log.verbosity == 'vv'

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), 0, None)
        >>> assert vq_log.verbosity is None

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), None, None)
        >>> assert vq_log.verbosity is None

        ``int`` can be supplied for quietness value
        -------------------------------------------

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), None, 2)
        >>> assert vq_log.quietness == 'qq'

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), None, 0)
        >>> assert vq_log.quietness is None

        >>> vq_log = VQSepLoggerConfigurator(StdLoggerConfigurator(), None, None)
        >>> assert vq_log.quietness is None

        negative ints for verbosity or quietness are not supported
        ----------------------------------------------------------

        >>> VQSepLoggerConfigurator(StdLoggerConfigurator(), -1, None)
        Traceback (most recent call last):
        ValueError: 'verbosity' cannot be negative.

        >>> VQSepLoggerConfigurator(StdLoggerConfigurator(), None, -10)
        Traceback (most recent call last):
        ValueError: 'quietness' cannot be negative.

        over range ints produce warnings
        --------------------------------
        verbosity or quietness > 3 will produce warnings.

        :param configurator: The logger configurator to decorate.
        :param verbosity: verbosity level. Cannot be given with ``quietness``.
        :param quietness: quietness level. Cannot be given with ``verbosity``.
        :param vq_level_map: A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied. Assumes
            ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.
        :param vq_sep_configurator: verbosity quietness configurator. Defaults to ``VQSepExclusive``.
        :param default_log_level: log level when none of the verbosity or quietness is supplied.
        """
        self._vq_level_map = vq_level_map if vq_level_map else VQSepLoggerConfigurator.VQ_LEVEL_MAP
        self.vq_sep_configurator = vq_sep_configurator if vq_sep_configurator \
            else VQSepExclusive(self.vq_level_map, warn_only=True)
        c_verbosity = self.compute_verbosity(verbosity, {0: None, 1: 'v', 2: 'vv', 3: 'vvv'})
        c_quietness = self.compute_quietness(quietness, {0: None, 1: 'q', 2: 'qq', 3: 'qqq'})
        self.vq_sep_configurator.validate(c_verbosity, c_quietness)
        self.configurator = configurator
        self.verbosity = c_verbosity
        self.quietness = c_quietness
        self._underlying_configurator = self.configurator
        self.default_log_level = default_log_level

    @override
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        int_level = self.vq_sep_configurator.get_effective_level(self.verbosity, self.quietness, self.default_log_level)
        self.configurator.set_level(int_level)
        return self.configurator.configure(logger)

    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[VQLoggerConfigurator.T]:
        return self._vq_level_map

    @property
    def underlying_configurator(self) -> LoggerConfigurator:
        return self._underlying_configurator

    @override
    def clone_with(self, **kwargs) -> 'VQSepLoggerConfigurator':
        """
        kwargs:
            ``configurator`` - The logger configurator to decorate.

            ``verbosity`` - verbosity level. Cannot be given with ``quietness``.

            ``quietness`` - quietness level. Cannot be given with ``verbosity``.

            ``vq_level_map`` - A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied.
            Assumes ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.

            ``vq_sep_configurator`` - verbosity quietness configurator. Defaults to ``VQSepExclusive``.

            ``default_log_level`` - log level when none of the verbosity or quietness is supplied.
        :return: a new ``VQSepLoggerConfigurator``.
        """
        configurator = kwargs.pop('configurator', self.configurator)
        verbosity = kwargs.pop('verbosity', self.verbosity)
        quietness = kwargs.pop('quietness', self.quietness)
        vq_level_map = kwargs.pop('vq_level_map', self.vq_level_map)
        vq_sep_configurator = kwargs.pop('vq_sep_configurator', self.vq_sep_configurator)
        default_log_level = kwargs.pop('default_log_level', self.default_log_level)
        return VQSepLoggerConfigurator(configurator, verbosity, quietness, vq_level_map, vq_sep_configurator,
                                       default_log_level)

    @classmethod
    def compute_verbosity(cls, entity: int | V_LITERAL | None, entity_map: dict[int, V_LITERAL | None]) -> V_LITERAL | None:
        return cls._compute_entity(entity, 'verbosity', entity_map)

    @classmethod
    def compute_quietness(cls, entity: int | Q_LITERAL | None, entity_map: dict[int, Q_LITERAL | None]) -> Q_LITERAL | None:
        return cls._compute_entity(entity, 'quietness', entity_map)

    @classmethod
    def _compute_entity(cls, entity, emphasis: str, entity_map: dict):
        if isinstance(entity, int):
            int_entity = int(entity)
            if int_entity < 0:
                raise ValueError(f"'{emphasis}' cannot be negative.")
            max_int_entity = max(entity_map)
            if int_entity > max_int_entity:
                vt_warn(f"Supplied {emphasis}: '{int_entity}' is greater than the max supported "
                        f"{emphasis}: '{max_int_entity}'. Defaulting to max {emphasis}.")
                int_entity = max_int_entity
            return entity_map[int_entity]
        else:
            return entity


class VQCommLoggerConfigurator(VQLoggerConfigurator, LevelLoggerConfigurator[V_LITERAL | Q_LITERAL | None]):

    VQ_LEVEL_MAP_NONE = None
    VQ_COMM_CONF_NONE = None
    LOG_LEVEL_WARNING = VQLoggerConfigurator.LOG_LEVEL_WARNING

    def __init__(self, ver_qui: V_LITERAL | Q_LITERAL | None,
                 configurator: LevelLoggerConfigurator[VQLoggerConfigurator.T],
                 vq_level_map: VQ_DICT_LITERAL[VQLoggerConfigurator.T] | None = VQ_LEVEL_MAP_NONE,
                 vq_comm_configurator: VQCommConfigurator[VQLoggerConfigurator.T] | None = VQ_COMM_CONF_NONE,
                 default_log_level: VQLoggerConfigurator.T = LOG_LEVEL_WARNING):
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
        self.vq_comm_configurator = vq_comm_configurator if vq_comm_configurator \
            else VQCommon(self.vq_level_map, warn_only=True)
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

    @override
    @property
    def level(self) -> V_LITERAL | Q_LITERAL | None:
        return self.ver_qui

    @override
    def clone_with(self, **kwargs) -> 'VQCommLoggerConfigurator':
        """
        kwargs:
            ``configurator`` - The logger configurator to decorate.

            ``ver_qui`` - verbosity or quietness level.

            ``vq_level_map`` - A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied.
            Assumes ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.

            ``vq_comm_configurator`` - verbosity quietness configurator. Defaults to ``VQCommon``.

            ``default_log_level`` - log level when none of the verbosity or quietness is supplied.
        :return: a new ``VQCommLoggerConfigurator``.
        """
        configurator = kwargs.pop('configurator', self.configurator)
        ver_qui = kwargs.pop('ver_qui', self.ver_qui)
        vq_level_map = kwargs.pop('vq_level_map', self.vq_level_map)
        vq_comm_configurator = kwargs.pop('vq_comm_configurator', self.vq_comm_configurator)
        default_log_level = kwargs.pop('default_log_level', self.default_log_level)
        return VQCommLoggerConfigurator(ver_qui, configurator, vq_level_map, vq_comm_configurator, default_log_level)
