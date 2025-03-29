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
from abc import ABC
from logging import Logger
from typing import override, cast

from vt.utils.logging.logging import AllLevelLogger
from vt.utils.logging.logging.delegating.base import BaseDelegatingLogger
from vt.utils.logging.logging.std_log import StdLogProtocol, StdLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import ProtocolStdLevelLoggerImpl, \
    BaseDirectStdLevelLoggerImpl, BaseDirectAllLevelLoggerImpl


class BaseProtocolStdLevelLogger(BaseDelegatingLogger, StdLevelLogger, ABC):
    def __init__(self, logger_impl: ProtocolStdLevelLoggerImpl):
        self._logger_impl = logger_impl
        self._underlying_logger = self._logger_impl.underlying_logger
        self.name = self._logger_impl.underlying_logger.name
        self.level = self._logger_impl.underlying_logger.level
        self.disabled = self._logger_impl.underlying_logger.disabled

    @property
    def logger_impl(self) -> ProtocolStdLevelLoggerImpl:
        return self._logger_impl

    @override
    @property
    def underlying_logger(self) -> StdLogProtocol:
        return self._underlying_logger

    @override
    def debug(self, msg, *args, **kwargs) -> None:
        self.logger_impl.debug(msg, *args, **kwargs)

    @override
    def info(self, msg, *args, **kwargs) -> None:
        self.logger_impl.info(msg, *args, **kwargs)

    @override
    def warning(self, msg, *args, **kwargs) -> None:
        self.logger_impl.warning(msg, *args, **kwargs)

    @override
    def error(self, msg, *args, **kwargs) -> None:
        self.logger_impl.error(msg, *args, **kwargs)

    @override
    def critical(self, msg, *args, **kwargs) -> None:
        self.logger_impl.critical(msg, *args, **kwargs)

    @override
    def fatal(self, msg, *args, **kwargs) -> None:
        self.logger_impl.fatal(msg, *args, **kwargs)

    @override
    def exception(self, msg, *args, **kwargs) -> None:
        self.logger_impl.exception(msg, *args, **kwargs)

    @override
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        self.logger_impl.log(level, msg, *args, **kwargs)


class ProtocolStdLevelLogger(BaseProtocolStdLevelLogger, ABC):
    def __init__(self, logger_impl: ProtocolStdLevelLoggerImpl):
        super().__init__(logger_impl)


class BaseDirectStdLevelLogger(ProtocolStdLevelLogger, ABC):
    def __init__(self, logger_impl: BaseDirectStdLevelLoggerImpl):
        super().__init__(logger_impl)

    @property
    def logger_impl(self) -> BaseDirectStdLevelLoggerImpl:
        return cast(BaseDirectStdLevelLoggerImpl, self._logger_impl)

    @override
    @property
    def underlying_logger(self) -> Logger:
        return cast(Logger, self._underlying_logger)


class BaseDirectAllLevelLogger(BaseDirectStdLevelLogger, AllLevelLogger, ABC):
    def __init__(self, logger_impl: BaseDirectAllLevelLoggerImpl):
        super().__init__(logger_impl)

    @property
    def logger_impl(self) -> BaseDirectAllLevelLoggerImpl:
        return cast(BaseDirectAllLevelLoggerImpl, self._logger_impl)

    @override
    def trace(self, msg, *args, **kwargs) -> None:
        self.logger_impl.trace(msg, *args, **kwargs)

    @override
    def success(self, msg, *args, **kwargs) -> None:
        self.logger_impl.success(msg, *args, **kwargs)

    @override
    def notice(self, msg, *args, **kwargs) -> None:
        self.logger_impl.notice(msg, *args, **kwargs)
