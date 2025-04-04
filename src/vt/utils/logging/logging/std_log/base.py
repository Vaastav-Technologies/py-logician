#!/usr/bin/env python3
# coding=utf-8

"""
Logging interfaces for the standard logging library of python.
"""
from abc import abstractmethod
from logging import Logger, addLevelName
from typing import Protocol, Any, Mapping, override

from vt.utils.logging.logging import MinLogProtocol, AllLevelLogger
from vt.utils.logging.logging.base import FatalLogProtocol, ExceptionLogProtocol, HasUnderlyingLogger
from vt.utils.logging.logging.std_log import TRACE_LOG_LEVEL, TRACE_LOG_STR, SUCCESS_LOG_LEVEL, SUCCESS_LOG_STR, \
    NOTICE_LOG_LEVEL, NOTICE_LOG_STR, EXCEPTION_TRACEBACK_LOG_LEVEL, EXCEPTION_TRACEBACK_LOG_STR, FATAL_LOG_LEVEL, \
    FATAL_LOG_STR, CMD_LOG_LEVEL, CMD_LOG_STR


class StdLogProtocol(MinLogProtocol, Protocol):
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
    name: str
    level: int
    disabled: bool

    def fatal(self, msg: str, *args, **kwargs) -> None:
        ...

    # noinspection SpellCheckingInspection
    # required for the param stack-level because this method signature from the protocol needs to correctly match that
    # of the std logging method signature.
    def exception(self, msg: object, *args: object, exc_info: Any = ..., stack_info: bool = ...,
                  stacklevel: int = ..., extra: Mapping[str, object] | None = ...) -> None:
        ...


class StdLevelLogger(MinLogProtocol, FatalLogProtocol, ExceptionLogProtocol, HasUnderlyingLogger, Protocol):
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


class DirectStdAllLevelLogger(AllLevelLogger, Protocol):
    """
    All log levels as provided by the python std log.
    """
    DEFAULT_LEVEL_MAP: dict[int, str] = {TRACE_LOG_LEVEL: TRACE_LOG_STR,
                                         SUCCESS_LOG_LEVEL: SUCCESS_LOG_STR,
                                         NOTICE_LOG_LEVEL: NOTICE_LOG_STR,
                                         CMD_LOG_LEVEL: CMD_LOG_STR,
                                         EXCEPTION_TRACEBACK_LOG_LEVEL: EXCEPTION_TRACEBACK_LOG_STR,
                                         FATAL_LOG_LEVEL: FATAL_LOG_STR}

    @staticmethod
    def register_levels(level_name_map: dict[int, str] | None = None):
        """
        Register levels in the python std logger.

        Defaults to registering ``DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP`` if ``level_name_map`` is empty
        or ``None``.

        :param level_name_map: log level - name mapping.
        """
        level_name_map = level_name_map if level_name_map else DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP
        for l in level_name_map:
            addLevelName(l, level_name_map[l])

    @override
    @property
    @abstractmethod
    def underlying_logger(self) -> Logger: # noqa
        pass
