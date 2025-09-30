#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for standard Logger configurators.
"""

import logging
from typing import override, overload, Protocol, IO

from vt.utils.errors.warnings import vt_warn

from logician import DirectAllLevelLogger, DirectStdAllLevelLogger
from logician import errmsg_creator
from logician._repo import get_repo
from logician.configurators import (
    LoggerConfigurator,
    HasUnderlyingConfigurator,
    LevelLoggerConfigurator,
)
from logician.configurators.vq import (
    V_LITERAL,
    Q_LITERAL,
    VQ_DICT_LITERAL,
    VQConfigurator,
    VQSepConfigurator,
    VQCommConfigurator,
)
from logician.configurators.vq.comm import VQCommon
from logician.configurators.vq.sep import VQSepExclusive
from logician.format_mappers import StreamFormatMapperComputer
from logician.formatters import LogLevelFmt
from logician.stdlog import TRACE_LOG_LEVEL, FATAL_LOG_LEVEL, WARNING_LEVEL
from logician.stdlog.all_levels_impl import DirectAllLevelLoggerImpl
from logician.stdlog.format_mappers import StdStrFmtMprComputer
from logician.stdlog.hndlr_cfgr import HandlerConfigurator, SimpleHandlerConfigurator
from logician.stdlog.constants import (
    EX_LOG_LVL as E,
    LOG_LVL as L,
    LOG_FMT as F,
    LOG_STR_LVL as S,
)


class StdLoggerConfigurator(LevelLoggerConfigurator[E]):
    LOG_LEVEL_WARNING = WARNING_LEVEL
    CMD_NAME_NONE = None
    STREAM_FMT_MAPPER_NONE = None
    FMT_PER_LEVEL_NONE = None
    STREAM_SET_NONE = None
    LEVEL_NAME_MAP_NONE = None
    NO_WARN_FALSE = False
    PROPAGATE_FALSE = False

    @overload
    def __init__(
        self,
        *,
        level: E = LOG_LEVEL_WARNING,
        cmd_name: str | None = CMD_NAME_NONE,
        same_fmt_per_lvl: F | bool | None = FMT_PER_LEVEL_NONE,
        stream_set: set[IO] | None = STREAM_SET_NONE,
        level_name_map: dict[L, S] | None = LEVEL_NAME_MAP_NONE,
        no_warn: bool = NO_WARN_FALSE,
        propagate: bool = PROPAGATE_FALSE,
        handlr_cfgr: HandlerConfigurator = SimpleHandlerConfigurator(),
        stream_fmt_mapper_computer: StreamFormatMapperComputer[
            L, F
        ] = StdStrFmtMprComputer(),
    ): ...

    @overload
    def __init__(
        self,
        *,
        level: E = LOG_LEVEL_WARNING,
        cmd_name: str | None = CMD_NAME_NONE,
        stream_fmt_mapper: dict[IO, LogLevelFmt[L, F]] | None = STREAM_FMT_MAPPER_NONE,
        level_name_map: dict[L, S] | None = LEVEL_NAME_MAP_NONE,
        no_warn: bool = NO_WARN_FALSE,
        propagate: bool = PROPAGATE_FALSE,
        handlr_cfgr: HandlerConfigurator = SimpleHandlerConfigurator(),
        stream_fmt_mapper_computer: StreamFormatMapperComputer[
            L, F
        ] = StdStrFmtMprComputer(),
    ): ...

    def __init__(
        self,
        *,
        level: E = LOG_LEVEL_WARNING,
        cmd_name: str | None = CMD_NAME_NONE,
        stream_fmt_mapper: dict[IO, LogLevelFmt[L, F]] | None = STREAM_FMT_MAPPER_NONE,
        same_fmt_per_lvl: F | bool | None = FMT_PER_LEVEL_NONE,
        stream_set: set[IO] | None = STREAM_SET_NONE,
        level_name_map: dict[L, S] | None = LEVEL_NAME_MAP_NONE,
        no_warn: bool = NO_WARN_FALSE,
        propagate: bool = PROPAGATE_FALSE,
        handlr_cfgr: HandlerConfigurator = SimpleHandlerConfigurator(),
        stream_fmt_mapper_computer: StreamFormatMapperComputer[
            L, F
        ] = StdStrFmtMprComputer(),
    ):
        """
        Perform logger configuration using the python's std logger calls.

        ``L`` - python std log logging level type, typically ``int``.

        ``S`` - python std log logging level name type, typically ``str``.

        ``E`` - python std log extended logging level type, typically ``int | str``.

        ``F`` - python std log logging format type, typically ``str``.

        :param level: active logging level.
        :param cmd_name: The command name to register the command logging level to. If ``None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.
        :param stream_fmt_mapper: an output-stream -> log format mapper. Defaults to ``STDERR_ALL_LVL_DIFF_FMT`` if
            ``None`` is supplied. Cannot be used with ``same_fmt_per_lvl``
            and ``stream_set``. Note that ``{}`` denoting an empty ``stream_fmt_mapper`` is accepted and specifies
            the user's intent of not logging to any stream.
        :param same_fmt_per_lvl: Use same log format per logging level. A string argument can be passed to enforce
            that format across all levels. Cannot be provided with ``stream_fmt_mapper``.
        :param stream_set: set of streams to apply level formatting logic to. Cannot be provided with
            ``stream_fmt_mapper``. Note that ``{}`` denoting an empty stream_set is accepted and specifies
            the user's intent of not logging to any stream.
        :param level_name_map: log level - name mapping. This mapping updates the std python logging library's
            registered log levels . Check ``DirectAllLevelLogger.register_levels()`` for more info.
        :param no_warn: do not warn if a supplied level is not registered with the logging library.
        :param propagate: propagate logger records to parent loggers.
        :param handlr_cfgr: The configurator for logger's handlers. Strategy to configure logger's handlers to
            introduce formats on each stream.
        :param stream_fmt_mapper_computer: A computer that computes resulting ``stream_fmt_mapper`` from the supplied
            ``same_fmt_per_lvl`` and ``stream_set`` args.
        """
        self.validate_args(stream_fmt_mapper, stream_set, same_fmt_per_lvl)

        self._level = level
        self.cmd_name = cmd_name
        self.level_name_map = level_name_map
        self.handlr_cfgr = handlr_cfgr
        self.no_warn = no_warn
        self.propagate = propagate
        self.stream_fmt_mapper_computer = stream_fmt_mapper_computer
        if stream_fmt_mapper is not None:  # accepts empty i.e. falsy stream_fmt_mapper
            self.stream_fmt_mapper = stream_fmt_mapper
        else:
            self.stream_fmt_mapper = self.stream_fmt_mapper_computer.compute(
                same_fmt_per_lvl, stream_set
            )
        get_repo().init()

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
        levels_to_choose_from: dict[L, S] = DirectAllLevelLogger.register_levels(
            self.level_name_map
        )
        try:
            match level:
                case L():  # typically int
                    int_level = level
                case S():  # typically str
                    int_level = (
                        L(level)
                        if level.isdigit()
                        else logging.getLevelNamesMapping()[level]
                    )
                case None:
                    int_level = StdLoggerConfigurator.LOG_LEVEL_WARNING
                case _:
                    raise TypeError(
                        f"Wrong level value supplied: '{level}', Expected int or str, got "
                        f"{type(level).__name__}"
                    )
        except KeyError:
            if not self.no_warn:
                vt_warn(
                    f"{logger.name}: Undefined log level '{level}'. "
                    f"Choose from {list(levels_to_choose_from.values())}."
                )
                vt_warn(
                    f"{logger.name}: Setting log level to default: "
                    f"'{logging.getLevelName(StdLoggerConfigurator.LOG_LEVEL_WARNING)}'."
                )
            int_level = StdLoggerConfigurator.LOG_LEVEL_WARNING
        logger.setLevel(int_level)
        self.handlr_cfgr.configure(int_level, logger, stream_fmt_map)
        logger.propagate = self.propagate
        possible_level_str: E = logging.getLevelName(level)
        get_repo().index(
            logger.name,
            level=possible_level_str,
            propagate=self.propagate,
            logger="stdlog",
        )
        get_repo().commit()
        return DirectAllLevelLogger(
            DirectAllLevelLoggerImpl(logger), cmd_name=self.cmd_name
        )

    @override
    def set_level(self, new_level: E) -> E:
        orig_level = self.level
        self._level = new_level
        return orig_level

    @override
    @property
    def level(self) -> E:
        return self._level

    @override
    def clone(self, **overrides) -> "StdLoggerConfigurator":
        """
        overrides:
            ``level`` - active logging level.

            ``cmd_name`` - The command name to register the command logging level to. If ``None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.

            ``stream_fmt_mapper`` - an output-stream -> log format mapper. Defaults to ``STDERR_ALL_LVL_DIFF_FMT`` if
            ``None`` is supplied. Cannot be used with ``same_fmt_per_lvl``
            and ``stream_set``. Note that ``{}`` denoting an empty ``stream_fmt_mapper`` is accepted and specifies
            the user's intent of not logging to any stream.

            ``same_fmt_per_lvl`` - Use same log format per logging level. Cannot be provided with
            ``stream_fmt_mapper``.

            ``stream_set`` - set of streams to apply level formatting logic to. Cannot be provided with
            ``stream_fmt_mapper``.Note that ``{}`` denoting an empty stream_set is accepted and specifies the user's
            intent of not logging to any stream.

            ``level_name_map`` - log level - name mapping. This mapping updates the std python logging library's
            registered log levels . Check ``DirectAllLevelLogger.register_levels()`` for more info.

            ``no_warn`` - do not warn if a supplied level is not registered with the logging library.

            ``propagate`` - propagate logger records to parent loggers.

            ``handlr_cfgr`` - The configurator for logger's handlers. Strategy to configure logger's handlers to
            introduce formats on each stream. Check ``logician.stdlog.utils:simple_handlr_cfgr()`` for more info.

            ``stream_fmt_mapper_computer`` - A computer that computes resulting ``stream_fmt_mapper`` from the supplied
            ``same_fmt_per_lvl`` and ``stream_set`` args.
        :return: new ``StdLoggerConfigurator`` with supplied overrides.
        """
        level = overrides.pop("level", self.level)
        cmd_name = overrides.pop("cmd_name", self.cmd_name)
        same_fmt_per_lvl = overrides.pop(
            "same_fmt_per_lvl", StdLoggerConfigurator.FMT_PER_LEVEL_NONE
        )
        stream_set = overrides.pop("stream_set", StdLoggerConfigurator.STREAM_SET_NONE)
        stream_fmt_mapper = overrides.pop("stream_fmt_mapper", None)
        self.validate_args(stream_fmt_mapper, stream_set, same_fmt_per_lvl)
        stream_fmt_mapper = (
            stream_fmt_mapper
            if stream_fmt_mapper is not None
            else self.stream_fmt_mapper
        )
        level_name_map = overrides.pop("level_name_map", self.level_name_map)
        no_warn = overrides.pop("no_warn", self.no_warn)
        propagate = overrides.pop("propagate", StdLoggerConfigurator.PROPAGATE_FALSE)
        handlr_cfgr = overrides.pop("handlr_cfgr", self.handlr_cfgr)
        stream_fmt_mapper_computer = overrides.pop(
            "stream_fmt_mapper_computer", self.stream_fmt_mapper_computer
        )
        if stream_fmt_mapper is not None:
            return StdLoggerConfigurator(
                level=level,
                cmd_name=cmd_name,
                stream_fmt_mapper=stream_fmt_mapper,
                level_name_map=level_name_map,
                no_warn=no_warn,
                propagate=propagate,
                handlr_cfgr=handlr_cfgr,
                stream_fmt_mapper_computer=stream_fmt_mapper_computer,
            )
        else:
            return StdLoggerConfigurator(
                level=level,
                cmd_name=cmd_name,
                stream_set=stream_set,
                same_fmt_per_lvl=same_fmt_per_lvl,
                level_name_map=level_name_map,
                no_warn=no_warn,
                propagate=propagate,
                handlr_cfgr=handlr_cfgr,
                stream_fmt_mapper_computer=stream_fmt_mapper_computer,
            )

    @staticmethod
    def validate_args(
        stream_fmt_mapper: dict[IO, LogLevelFmt[L, F]] | None,
        stream_set: set[IO] | None,
        same_fmt_per_lvl: F | bool | None,
    ):
        """
        :raises ValueError: if  ``stream_fmt_mapper`` is given with ``stream_set`` or
            if  ``stream_fmt_mapper`` is given with ``same_fmt_per_lvl``.
        """
        if stream_fmt_mapper is not None and stream_set is not None:
            raise ValueError(
                errmsg_creator.not_allowed_together("stream_fmt_mapper", "stream_set")
            )
        if stream_fmt_mapper is not None and same_fmt_per_lvl is not None:
            raise ValueError(
                errmsg_creator.not_allowed_together(
                    "stream_fmt_mapper", "same_fmt_per_lvl"
                )
            )


class VQLoggerConfigurator(
    LoggerConfigurator, VQConfigurator[E], HasUnderlyingConfigurator, Protocol
):
    """
    Logger configurator that can decorate other configurators to set their underlying logger levels. This log level is
    to be set according to the supplied verbosity and quietness values.

        ``L`` - python std log logging level type, typically ``int``.

        ``S`` - python std log logging level name type, typically ``str``.

        ``E`` - python std log extended logging level type, typically ``int | str``.

        ``F`` - python std log logging format type, typically ``str``.
    """

    VQ_LEVEL_MAP: VQ_DICT_LITERAL[E] = dict(
        v=logging.INFO,
        vv=logging.DEBUG,
        vvv=TRACE_LOG_LEVEL,
        q=logging.ERROR,
        qq=logging.CRITICAL,
        qqq=FATAL_LOG_LEVEL,
    )
    """
    Default {``verbosity-quietness -> logging-level``} mapping.
    """
    LOG_LEVEL_WARNING: E = WARNING_LEVEL


class VQSepLoggerConfigurator(VQLoggerConfigurator):
    VQ_LEVEL_MAP_NONE = None
    VQ_SEP_CONF_NONE = None
    LOG_LEVEL_WARNING = VQLoggerConfigurator.LOG_LEVEL_WARNING

    @overload
    def __init__(
        self,
        configurator: LevelLoggerConfigurator[E],
        verbosity: int | None,
        quietness: int | None,
        vq_level_map: VQ_DICT_LITERAL[E] | None = VQ_LEVEL_MAP_NONE,
        vq_sep_configurator: VQSepConfigurator[E] | None = VQ_SEP_CONF_NONE,
        default_log_level: E = LOG_LEVEL_WARNING,
    ): ...

    @overload
    def __init__(
        self,
        configurator: LevelLoggerConfigurator[E],
        verbosity: V_LITERAL | None,
        quietness: Q_LITERAL | None,
        vq_level_map: VQ_DICT_LITERAL[E] | None = VQ_LEVEL_MAP_NONE,
        vq_sep_configurator: VQSepConfigurator[E] | None = VQ_SEP_CONF_NONE,
        default_log_level: E = LOG_LEVEL_WARNING,
    ): ...

    def __init__(
        self,
        configurator: LevelLoggerConfigurator[E],
        verbosity: V_LITERAL | int | None,
        quietness: Q_LITERAL | int | None,
        vq_level_map: VQ_DICT_LITERAL[E] | None = VQ_LEVEL_MAP_NONE,
        vq_sep_configurator: VQSepConfigurator[E] | None = VQ_SEP_CONF_NONE,
        default_log_level: E = LOG_LEVEL_WARNING,
    ):
        """
        A logger configurator that can decorate another logger configurator to accept and infer logging level based on
        ``verbosity`` and ``quietness`` values.

        ``L`` - python std log logging level type, typically ``int``.

        ``S`` - python std log logging level name type, typically ``str``.

        ``E`` - python std log extended logging level type, typically ``int | str``.

        ``F`` - python std log logging format type, typically ``str``.

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
        >>> assert vq_log.underlying_configurator.level == vq_log.default_log_level

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
        self._vq_level_map = (
            vq_level_map if vq_level_map else VQSepLoggerConfigurator.VQ_LEVEL_MAP
        )
        self.vq_sep_configurator = (
            vq_sep_configurator
            if vq_sep_configurator
            else VQSepExclusive(self.vq_level_map, warn_only=True)
        )
        c_verbosity = self.compute_verbosity(
            verbosity, {0: None, 1: "v", 2: "vv", 3: "vvv"}
        )
        c_quietness = self.compute_quietness(
            quietness, {0: None, 1: "q", 2: "qq", 3: "qqq"}
        )
        self.vq_sep_configurator.validate(c_verbosity, c_quietness)
        self._underlying_configurator = configurator
        self.verbosity = c_verbosity
        self.quietness = c_quietness
        self.default_log_level = default_log_level

    @override
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        # TODO: write extensive tests for the
        #  self.underlying_configurator.level or self.default_log_level
        #  logic
        int_level = self.vq_sep_configurator.get_effective_level(
            self.verbosity,
            self.quietness,
            self.underlying_configurator.level or self.default_log_level,
        )
        self.underlying_configurator.set_level(int_level)
        get_repo().index(
            logger.name,
            level=int_level,
            verbosity=self.verbosity,
            quietness=self.quietness,
        )
        return self.underlying_configurator.configure(logger)

    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[E]:
        return self._vq_level_map

    @override
    @property
    def underlying_configurator(self) -> LevelLoggerConfigurator[E]:
        return self._underlying_configurator  # pragma: no cover

    @override
    def clone(self, **overrides) -> "VQSepLoggerConfigurator":
        """
        overrides:
            ``configurator`` - The logger configurator to decorate.

            ``verbosity`` - verbosity level. Cannot be given with ``quietness``.

            ``quietness`` - quietness level. Cannot be given with ``verbosity``.

            ``vq_level_map`` - A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied.
            Assumes ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.

            ``vq_sep_configurator`` - verbosity quietness configurator. Defaults to ``VQSepExclusive``.

            ``default_log_level`` - log level when none of the verbosity or quietness is supplied.
        :return: a new ``VQSepLoggerConfigurator``.
        """
        configurator = overrides.pop("configurator", self.underlying_configurator)
        verbosity = overrides.pop("verbosity", self.verbosity)
        quietness = overrides.pop("quietness", self.quietness)
        vq_level_map = overrides.pop("vq_level_map", self.vq_level_map)
        vq_sep_configurator = overrides.pop(
            "vq_sep_configurator", self.vq_sep_configurator
        )
        default_log_level = overrides.pop("default_log_level", self.default_log_level)
        return VQSepLoggerConfigurator(
            configurator,
            verbosity,
            quietness,
            vq_level_map,
            vq_sep_configurator,
            default_log_level,
        )

    @classmethod
    def compute_verbosity(
        cls, entity: int | V_LITERAL | None, entity_map: dict[int, V_LITERAL | None]
    ) -> V_LITERAL | None:
        return cls._compute_entity(entity, "verbosity", entity_map)

    @classmethod
    def compute_quietness(
        cls, entity: int | Q_LITERAL | None, entity_map: dict[int, Q_LITERAL | None]
    ) -> Q_LITERAL | None:
        return cls._compute_entity(entity, "quietness", entity_map)

    @classmethod
    def _compute_entity(cls, entity, emphasis: str, entity_map: dict):
        if isinstance(entity, int):
            int_entity = int(entity)
            if int_entity < 0:
                raise ValueError(f"'{emphasis}' cannot be negative.")
            max_int_entity = max(entity_map)
            if int_entity > max_int_entity:
                vt_warn(
                    f"Supplied {emphasis}: '{int_entity}' is greater than the max supported "
                    f"{emphasis}: '{max_int_entity}'. Defaulting to max {emphasis}."
                )
                int_entity = max_int_entity
            return entity_map[int_entity]
        else:
            return entity


class VQCommLoggerConfigurator(
    VQLoggerConfigurator, LevelLoggerConfigurator[V_LITERAL | Q_LITERAL | None]
):
    VQ_LEVEL_MAP_NONE = None
    VQ_COMM_CONF_NONE = None
    LOG_LEVEL_WARNING = VQLoggerConfigurator.LOG_LEVEL_WARNING

    def __init__(
        self,
        ver_qui: V_LITERAL | Q_LITERAL | None,
        configurator: LevelLoggerConfigurator[E],
        vq_level_map: VQ_DICT_LITERAL[E] | None = VQ_LEVEL_MAP_NONE,
        vq_comm_configurator: VQCommConfigurator[E] | None = VQ_COMM_CONF_NONE,
        default_log_level: E = LOG_LEVEL_WARNING,
    ):
        """
        A logger configurator that can decorate another logger configurator to accept and infer logging level based on
        ``verbosity`` or ``quietness`` values.

        ``L`` - python std log logging level type, typically ``int``.

        ``S`` - python std log logging level name type, typically ``str``.

        ``E`` - python std log extended logging level type, typically ``int | str``.

        ``F`` - python std log logging format type, typically ``str``.

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
        self._vq_level_map = (
            vq_level_map if vq_level_map else VQCommLoggerConfigurator.VQ_LEVEL_MAP
        )
        self.vq_comm_configurator = (
            vq_comm_configurator
            if vq_comm_configurator
            else VQCommon(self.vq_level_map, warn_only=True)
        )
        self.vq_comm_configurator.validate(ver_qui)
        self._underlying_configurator = configurator
        self.ver_qui = ver_qui
        self.default_log_level = default_log_level

    @override
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        # TODO: write extensive tests for the
        #  self.underlying_configurator.level or self.default_log_level
        #  logic
        int_level = self.vq_comm_configurator.get_effective_level(
            self.ver_qui, self.underlying_configurator.level or self.default_log_level
        )
        get_repo().index(logger.name, vq=self.ver_qui, level=int_level)
        self.underlying_configurator.set_level(int_level)
        return self.underlying_configurator.configure(logger)

    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[E]:
        return self._vq_level_map

    @property
    def underlying_configurator(
        self,
    ) -> LevelLoggerConfigurator[E]:
        return self._underlying_configurator  # pragma: no cover

    @override
    def set_level(
        self, new_ver_qui: V_LITERAL | Q_LITERAL | None
    ) -> V_LITERAL | Q_LITERAL | None:
        orig_ver_qui = self.ver_qui
        self.ver_qui = new_ver_qui
        return orig_ver_qui

    @override
    @property
    def level(self) -> V_LITERAL | Q_LITERAL | None:
        return self.ver_qui

    @override
    def clone(self, **overrides) -> "VQCommLoggerConfigurator":
        """
        overrides:
            ``configurator`` - The logger configurator to decorate.

            ``ver_qui`` - verbosity or quietness level.

            ``vq_level_map`` - A user defined {``verbosity-quietness -> logging-level``} mapping can be supplied.
            Assumes ``VQLoggerConfigurator.VQ_LEVEL_MAP`` when omitted or ``None`` is supplied.

            ``vq_comm_configurator`` - verbosity quietness configurator. Defaults to ``VQCommon``.

            ``default_log_level`` - log level when none of the verbosity or quietness is supplied.
        :return: a new ``VQCommLoggerConfigurator``.
        """
        configurator = overrides.pop("configurator", self.underlying_configurator)
        ver_qui = overrides.pop("ver_qui", self.ver_qui)
        vq_level_map = overrides.pop("vq_level_map", self.vq_level_map)
        vq_comm_configurator = overrides.pop(
            "vq_comm_configurator", self.vq_comm_configurator
        )
        default_log_level = overrides.pop("default_log_level", self.default_log_level)
        return VQCommLoggerConfigurator(
            ver_qui, configurator, vq_level_map, vq_comm_configurator, default_log_level
        )
