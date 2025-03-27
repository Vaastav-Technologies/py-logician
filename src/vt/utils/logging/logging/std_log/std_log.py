#!/usr/bin/env python3
# coding=utf-8

"""
Logging interface implementation by the standard logging library of python.
"""
import logging
from abc import ABC
from logging import Logger
from typing import override

from vt.utils.logging.logging.std_log import StdLevelLogger, StdLogProtocol
from vt.utils.logging.logging.std_log.__constants__ import DEFAULT_STACK_LEVEL


class _BaseStdLevelLogger(StdLevelLogger, ABC):

    def __init__(self, underlying_logger: StdLogProtocol):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        self._underlying_logger = underlying_logger
        self.name = underlying_logger.name
        self.level = underlying_logger.level
        self.disabled = underlying_logger.disabled

    @override
    @property
    def underlying_logger(self) -> StdLogProtocol:
        return self._underlying_logger

    @override
    def debug(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.debug(msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def info(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.info(msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def warning(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.warning(msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def error(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.error(msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def critical(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.critical(msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def fatal(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.fatal(msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def exception(self, msg, *args, **kwargs) -> None:
        self.underlying_logger.exception(msg, *args, exc_info=True, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)

    @override
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        self.underlying_logger.log(level, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs)


class BasicStdProtocolLevelLogger(_BaseStdLevelLogger):

    def __init__(self, underlying_logger: StdLogProtocol):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger)


BasicStdProtocolLevelLogger(logging.getLogger())


class BasicStdLevelLogger(_BaseStdLevelLogger):

    def __init__(self, underlying_logger: Logger):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger) # noqa

    @override
    @property
    def underlying_logger(self) -> Logger:
        return self._underlying_logger
