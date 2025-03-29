#!/usr/bin/env python3
# coding=utf-8

"""
Classes w.r.t implementation inheritance are defined here.
"""
from abc import ABC
from logging import Logger
from typing import override, cast

from vt.utils.logging.logging.bridge.base_impl import ProtocolMinLevelLoggerImplABC, AllLevelLoggerImplABC
from vt.utils.logging.logging.std_log import TRACE_LOG_LEVEL, \
    NOTICE_LOG_LEVEL, SUCCESS_LOG_LEVEL, StdLevelLogger, StdLogProtocol, INDIRECTION_STACK_LEVEL


class ProtocolStdLevelLoggerImpl(ProtocolMinLevelLoggerImplABC, StdLevelLogger, ABC):

    def __init__(self, underlying_logger: StdLogProtocol):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger. Created for implementation inheritance.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        self._underlying_logger = underlying_logger

    @override
    @property
    def underlying_logger(self) -> StdLogProtocol:
        return self._underlying_logger


class BaseDirectStdLevelLoggerImpl(ProtocolStdLevelLoggerImpl, ABC): # implementation inheritance, not is-a

    def __init__(self, underlying_logger: Logger):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger. Created for implementation inheritance.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger) # noqa

    @override
    @property
    def underlying_logger(self) -> Logger:
        return cast(Logger, self._underlying_logger)


class BaseDirectAllLevelLoggerImpl(BaseDirectStdLevelLoggerImpl, AllLevelLoggerImplABC, ABC): # implementation
    # inheritance, not is-a

    def __init__(self, underlying_logger: Logger):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger. Created for implementation inheritance.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger)


class DirectStdLevelLoggerImpl(BaseDirectStdLevelLoggerImpl):

    def __init__(self, underlying_logger: Logger, stack_level=INDIRECTION_STACK_LEVEL):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger. Created for implementation inheritance.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger) # noqa
        self.stack_level = stack_level

    @override
    @property
    def underlying_logger(self) -> Logger:
        return cast(Logger, self._underlying_logger)

    @override
    def debug(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.debug(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def info(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.info(msg, *args, stacklevel=self.stack_level, **kwargs)

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
        self.underlying_logger.fatal(msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def exception(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.exception(msg, *args, exc_info=True, stacklevel=self.stack_level, **kwargs)

    @override
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        self.underlying_logger.log(level, msg, *args, stacklevel=self.stack_level, **kwargs)


class DirectAllLevelLoggerImpl(DirectStdLevelLoggerImpl, # implementation inheritance, not is-a
                               AllLevelLoggerImplABC):

    def __init__(self, underlying_logger: Logger, stack_level=INDIRECTION_STACK_LEVEL):
        super().__init__(underlying_logger, stack_level)

    @override
    def trace(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(TRACE_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def success(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(SUCCESS_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)

    @override
    def notice(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.log(NOTICE_LOG_LEVEL, msg, *args, stacklevel=self.stack_level, **kwargs)
