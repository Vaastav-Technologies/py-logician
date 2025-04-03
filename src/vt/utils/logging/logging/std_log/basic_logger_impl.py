#!/usr/bin/env python3
# coding=utf-8

"""
Classes w.r.t implementation inheritance are defined here.
"""
from abc import abstractmethod
from logging import Logger
from typing import override, cast, Protocol

from vt.utils.logging.logging.delegating import AllLevelLoggerImplABC
from vt.utils.logging.logging.std_log import TRACE_LOG_LEVEL, \
    NOTICE_LOG_LEVEL, SUCCESS_LOG_LEVEL, StdLogProtocol, INDIRECTION_STACK_LEVEL, FATAL_LOG_LEVEL


class StdProtocolAllLevelLoggerImpl(AllLevelLoggerImplABC, Protocol):
    """
    Interface for all logging levels provided by the standard logging protocol.
    """

    @override
    @property
    @abstractmethod
    def underlying_logger(self) -> StdLogProtocol:
        pass


class BaseDirectStdAllLevelLoggerImpl(StdProtocolAllLevelLoggerImpl, Protocol):
    """
    Interface for all logging levels provided by the python standard logging library.
    """

    @override
    @property
    @abstractmethod
    def underlying_logger(self) -> Logger: # noqa
        pass


class DirectAllLevelLoggerImpl(BaseDirectStdAllLevelLoggerImpl):

    def __init__(self, underlying_logger: Logger, stack_level=INDIRECTION_STACK_LEVEL):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger. Created for implementation inheritance.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        self._underlying_logger = underlying_logger
        self.stack_level = stack_level

    @override
    @property
    def underlying_logger(self) -> Logger: # noqa
        return cast(Logger, self._underlying_logger)

    @override
    def trace(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(TRACE_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def debug(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.debug(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def info(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.info(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def success(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(SUCCESS_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def notice(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(NOTICE_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def warning(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.warning(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def error(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.error(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def critical(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.critical(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def fatal(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(FATAL_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def exception(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.exception(msg, *args, exc_info=True, stacklevel=self.stack_level, **kwargs)

    @override
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        self.underlying_logger.log(level, msg, *args, stacklevel=self.stack_level, **kwargs)
