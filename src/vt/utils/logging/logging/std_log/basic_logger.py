#!/usr/bin/env python3
# coding=utf-8

"""
Basic logging interface implementation by the standard logging library of python.

Basic loggers only support operations::

    - log
    - debug
    - info
    - warning
    - error
    - exception
    - critical
    - fatal
"""
from logging import Logger
from typing import override, cast
from abc import ABC

from vt.utils.logging.logging import MinLogProtocol
from vt.utils.logging.logging.std_log import StdLogProtocol, StdLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import BaseStdLevelLoggerImpl


class _StdLevelLogger(StdLevelLogger, ABC):
    def __init__(self, logger_impl: BaseStdLevelLoggerImpl[StdLogProtocol]):
        """
        Logger that implements all the logging levels of python standard logging PROTOCOL and simply delegates
        method calls to the underlying logger.

        :param underlying_logger: logger (python standard logger logging PROTOCOL) that actually performs the logging.
        """
        self.logger_impl = logger_impl
        self._underlying_logger = logger_impl.underlying_logger

    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        return self.underlying_logger.log(level, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs) -> None:
        return self.underlying_logger.debug(msg, *args, **kwargs)


class ProtocolStdLevelLogger(StdLevelLogger, _StdLevelLogger): # implementation inheritance, not is-a

    def __init__(self, logger_impl: BaseStdLevelLoggerImpl[StdLogProtocol]):
        """
        Logger that implements all the logging levels of python standard logging PROTOCOL and simply delegates
        method calls to the underlying logger.

        :param underlying_logger: logger (python standard logger logging PROTOCOL) that actually performs the logging.
        """
        super().__init__(logger_impl)

    @property
    def underlying_logger(self) -> StdLogProtocol:
        return self._underlying_logger


class DirectStdLevelLogger(StdLevelLogger, _StdLevelLogger): # implementation inheritance, not is-a

    def __init__(self, logger_impl: BaseStdLevelLoggerImpl[Logger]):
        """
        Logger that implements all the logging levels of python standard logging DIRECTLY. It simply delegates method
        calls to the underlying logger.

        :param underlying_logger: logger (actual python standard logger) that actually performs the logging.
        """
        super().__init__(logger_impl) # noqa

    @override
    @property
    def underlying_logger(self) -> Logger:
        return cast(Logger, self.underlying_logger)
