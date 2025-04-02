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
import logging
from abc import ABC
from logging import Logger
from typing import override, cast

from vt.utils.logging.logging import AllLevelLogger
from vt.utils.logging.logging.delegating import BaseDelegatingLogger
from vt.utils.logging.logging.std_log import StdLogProtocol, TRACE_LOG_LEVEL, TRACE_LOG_STR, \
    SUCCESS_LOG_LEVEL, SUCCESS_LOG_STR, NOTICE_LOG_LEVEL, NOTICE_LOG_STR, EXCEPTION_TRACEBACK_LOG_LEVEL, \
    EXCEPTION_TRACEBACK_LOG_STR, FATAL_LOG_LEVEL, FATAL_LOG_STR
from vt.utils.logging.logging.std_log.basic_logger_impl import StdProtocolAllLevelLoggerImpl, \
    BaseDirectStdAllLevelLoggerImpl, BaseDirectAllLevelLoggerImpl


class BaseStdProtocolAllLevelLogger(AllLevelLogger, BaseDelegatingLogger, ABC):
    def __init__(self, logger_impl: StdProtocolAllLevelLoggerImpl):
        self._logger_impl = logger_impl
        self._underlying_logger = self._logger_impl.underlying_logger
        self.name = self._logger_impl.underlying_logger.name
        self.level = self._logger_impl.underlying_logger.level
        self.disabled = self._logger_impl.underlying_logger.disabled

    @property
    def logger_impl(self) -> StdProtocolAllLevelLoggerImpl:
        return self._logger_impl

    @override
    @property
    def underlying_logger(self) -> StdLogProtocol:
        return self._underlying_logger

    @override
    def trace(self, msg, *args, **kwargs) -> None:
        self.logger_impl.trace(msg, *args, **kwargs)

    @override
    def debug(self, msg, *args, **kwargs) -> None:
        self.logger_impl.debug(msg, *args, **kwargs)

    @override
    def info(self, msg, *args, **kwargs) -> None:
        self.logger_impl.info(msg, *args, **kwargs)

    @override
    def notice(self, msg, *args, **kwargs) -> None:
        self.logger_impl.notice(msg, *args, **kwargs)

    @override
    def success(self, msg, *args, **kwargs) -> None:
        self.logger_impl.success(msg, *args, **kwargs)

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


class StdProtocolAllLevelLogger(BaseStdProtocolAllLevelLogger, ABC):
    def __init__(self, logger_impl: StdProtocolAllLevelLoggerImpl):
        super().__init__(logger_impl)


class BaseDirectStdAllLevelLogger(BaseStdProtocolAllLevelLogger, ABC):
    DEFAULT_LEVEL_MAP: dict[int, str] = {TRACE_LOG_LEVEL: TRACE_LOG_STR,
                                         SUCCESS_LOG_LEVEL: SUCCESS_LOG_STR,
                                         NOTICE_LOG_LEVEL: NOTICE_LOG_STR,
                                         EXCEPTION_TRACEBACK_LOG_LEVEL: EXCEPTION_TRACEBACK_LOG_STR,
                                         FATAL_LOG_LEVEL: FATAL_LOG_STR}

    @staticmethod
    def register_levels(level_name_map: dict[int, str] | None = None):
        level_name_map = level_name_map if level_name_map else BaseDirectAllLevelLogger.DEFAULT_LEVEL_MAP
        for l in level_name_map:
            logging.addLevelName(l, level_name_map[l])

    def __init__(self, logger_impl: BaseDirectStdAllLevelLoggerImpl,
                 level_name_map: dict[int, str] | None = None):
        super().__init__(logger_impl)
        if level_name_map:
            BaseDirectStdAllLevelLogger.register_levels(level_name_map)
        self.level_name_map = level_name_map

    @property
    def logger_impl(self) -> BaseDirectStdAllLevelLoggerImpl:
        return cast(BaseDirectStdAllLevelLoggerImpl, self._logger_impl)

    @override
    @property
    def underlying_logger(self) -> Logger: # noqa
        return cast(Logger, self._underlying_logger)


class BaseDirectAllLevelLogger(BaseDirectStdAllLevelLogger, AllLevelLogger, ABC):

    def __init__(self, logger_impl: BaseDirectAllLevelLoggerImpl,
                 level_name_map: dict[int, str] | None = None):
        super().__init__(logger_impl, level_name_map)

    @property
    def logger_impl(self) -> BaseDirectAllLevelLoggerImpl:
        return cast(BaseDirectAllLevelLoggerImpl, self._logger_impl)
