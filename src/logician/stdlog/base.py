#!/usr/bin/env python3
# coding=utf-8

"""
Logging interfaces for the standard logging library of python.
"""

import logging
from abc import abstractmethod
from typing import Protocol, Any, Mapping, override

from logician import MinLogProtocol, AllLevelLogger
from logician.base import FatalLogProtocol, ExceptionLogProtocol, HasUnderlyingLogger
from logician.stdlog import (
    TRACE_LOG_LEVEL,
    TRACE_LOG_STR,
    SUCCESS_LOG_LEVEL,
    SUCCESS_LOG_STR,
    NOTICE_LOG_LEVEL,
    NOTICE_LOG_STR,
    EXCEPTION_TRACEBACK_LOG_LEVEL,
    EXCEPTION_TRACEBACK_LOG_STR,
    FATAL_LOG_LEVEL,
    FATAL_LOG_STR,
    CMD_LOG_LEVEL,
    CMD_LOG_STR,
)
from logician.stdlog.utils import level_name_mapping
from logician.stdlog.constants import LOG_LVL as L, LOG_STR_LVL as S


class StdLogProtocol(MinLogProtocol[L], Protocol):
    """
    Logger protocol that is followed (for methods) by the python std logging.

    Two additional methods are added on top of the MinLogProtocol::

        - fatal
        - exception

    along with properties that python std logger provides::

        - name
        - level
        - disabled
    """

    name: S
    level: L
    disabled: bool

    def fatal(self, msg: str, *args, **kwargs) -> None: ...

    # noinspection SpellCheckingInspection
    # required for the param stack-level because this method signature from the protocol needs to correctly match that
    # of the std logging method signature.
    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: Any = ...,
        stack_info: bool = ...,
        stacklevel: L = ...,
        extra: Mapping[str, object] | None = ...,
    ) -> None: ...


class StdLevelLogger(
    MinLogProtocol[L],
    FatalLogProtocol,
    ExceptionLogProtocol,
    HasUnderlyingLogger[L],
    Protocol,
):
    """
    Logger that implements python standard logging methods::

        - debug
        - info
        - warning
        - error
        - critical
        - fatal
        - exception
    """

    pass


class DirectStdAllLevelLogger(AllLevelLogger[L], Protocol):
    """
    All logging levels as provided by the python std logging.
    """

    DEFAULT_LEVEL_MAP: dict[L, S] = {
        TRACE_LOG_LEVEL: TRACE_LOG_STR,
        SUCCESS_LOG_LEVEL: SUCCESS_LOG_STR,
        NOTICE_LOG_LEVEL: NOTICE_LOG_STR,
        CMD_LOG_LEVEL: CMD_LOG_STR,
        EXCEPTION_TRACEBACK_LOG_LEVEL: EXCEPTION_TRACEBACK_LOG_STR,
        FATAL_LOG_LEVEL: FATAL_LOG_STR,
    }
    """
    All log levels in accordance with the python std log. Ordered in such a fashion::
    
        3 -> TRACEBACK
        5 -> TRACE
        10 -> DEBUG
        20 -> INFO
        23 -> SUCCESS
        26 -> NOTICE
        28 -> COMMAND
        30 -> WARNING
        40 -> ERROR
        50 -> CRITICAL
        60 -> FATAL
    """

    @staticmethod
    def register_levels(level_name_map: dict[L, S] | None = None) -> dict[L, S]:
        """
        Register levels in the python std logger.

        Note::

            The level changes are global in python std library hence, multiple calls to
            ``DirectStdAllLevelLogger.register_levels()`` may result in the latest call to win.

        * Examples:

          * Register more levels:

            >>> lvl_name_map = DirectStdAllLevelLogger.register_levels({1:"TRACE_DETAILED", 70: "BOMBED"})
            >>> assert lvl_name_map[1] == "TRACE_DETAILED"
            >>> assert lvl_name_map[70] == "BOMBED"

          * Change name for existing levels

            >>> lvl_name_map = level_name_mapping()
            >>> assert lvl_name_map[logging.DEBUG] == "DEBUG"
            >>> lvl_name_map = DirectStdAllLevelLogger.register_levels({logging.DEBUG: "DETAILED_INFO"})
            >>> assert lvl_name_map[logging.DEBUG] == "DETAILED_INFO" # DEBUG level name changed

          * Original (Default) levels kept if no levels are supplied:

            >>> lvl_name_map = DirectStdAllLevelLogger.register_levels()
            >>> assert all(lvl_name_map[lvl]==lvl_name for lvl, lvl_name in DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP.items())

          * Original (Default) levels kept if empty level dict is provided:

            >>> lvl_name_map = DirectStdAllLevelLogger.register_levels()
            >>> assert all(lvl_name_map[lvl]==lvl_name for lvl, lvl_name in DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP.items())

        :param level_name_map: log level - name mapping. This mapping updates the
            ``DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP`` and then all the updated
            ``DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP`` log levels are registered.
        :return: An ascending sorted level -> name map of all the registered log levels.
        """
        if level_name_map:
            DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP.update(level_name_map)
        DirectStdAllLevelLogger.__register_all_levels(
            DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP
        )
        return level_name_mapping()

    @staticmethod
    def __register_all_levels(level_name_map: dict[L, S]):
        for level in level_name_map:
            logging.addLevelName(level, level_name_map[level])

    @override
    @property
    @abstractmethod
    def underlying_logger(self) -> logging.Logger:  # noqa
        pass
