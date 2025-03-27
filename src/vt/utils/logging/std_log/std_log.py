#!/usr/bin/env python3
# coding=utf-8

"""
Logging interface implementation by the standard logging library of python.
"""
from typing import override, Protocol, Any, Mapping

from vt.utils.logging import StdLevelLogger, StdLogProtocol
from vt.utils.logging.std_log.__constants__ import DEFAULT_STACK_LEVEL


class StdStdLogProtocol(StdLogProtocol, Protocol):
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
