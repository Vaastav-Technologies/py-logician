#!/usr/bin/env python3
# coding=utf-8

"""
Logging interface implementation by the standard logging library of python
"""
import logging
from typing import Any, override

from vt.utils.logging import StdLevelLogger, AllLevelLogger, StdLogProtocol
from vt.utils.logging.std_log.__constants__ import DEFAULT_STACK_LEVEL


class StdStdLogProtocol(StdLogProtocol):
    name: str
    level: int
    disabled: bool

    def exception(self, msg, *args, **kwargs) -> None:
        ...


class BasicStdLevelLogger(StdLevelLogger):
    def __init__(self, underlying_logger:StdStdLogProtocol):
        self.__underlying_logger = underlying_logger
        self.name = underlying_logger.name
        self.level = underlying_logger.level
        self.disabled = underlying_logger.disabled

    @override
    @property
    def underlying_logger(self) -> StdStdLogProtocol:
        return self.__underlying_logger

    @override
    def debug(self, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.debug(msg, *args, stacklevel=stacklevel, **kwargs)

    @override
    def info(self, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.info(msg, *args, stacklevel=stacklevel, **kwargs)

    @override
    def warning(self, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.warning(msg, *args, stacklevel=stacklevel, **kwargs)

    @override
    def error(self, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.error(msg, *args, stacklevel=stacklevel, **kwargs)

    @override
    def critical(self, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.critical(msg, *args, stacklevel=stacklevel, **kwargs)

    @override
    def exception(self, msg, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.exception(msg, *args, stacklevel=stacklevel, **kwargs)

    @override
    def log(self, level: int, msg: str, *args, stacklevel=DEFAULT_STACK_LEVEL, **kwargs) -> None:
        self.underlying_logger.log(level, msg, *args, stacklevel=stacklevel, **kwargs)
