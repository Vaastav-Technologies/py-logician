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
from abc import ABC, abstractmethod
from logging import Logger
from typing import override, cast, Protocol

from vt.utils.logging.logging import AllLevelLogger
from vt.utils.logging.logging.delegating import DelegatingLogger
from vt.utils.logging.logging.std_log import StdLogProtocol
from vt.utils.logging.logging.std_log.base import DirectStdAllLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import StdProtocolAllLevelLoggerImpl, \
    BaseDirectStdAllLevelLoggerImpl


class StdProtocolAllLevelLogger(AllLevelLogger, DelegatingLogger, Protocol):
    """
    Interface for a std protocol logger which provides all logging levels by the protocol implementation.
    """

    @override
    @property
    @abstractmethod
    def logger_impl(self) -> StdProtocolAllLevelLoggerImpl:
        ...

    @override
    @property
    @abstractmethod
    def underlying_logger(self) -> StdLogProtocol:
        ...


class BaseStdProtocolAllLevelLogger(StdProtocolAllLevelLogger, ABC):
    def __init__(self, logger_impl: StdProtocolAllLevelLoggerImpl):
        """
        Implementation for a std protocol logger which provides all logging levels by the protocol implementation.

        see ``StdProtocolAllLevelLoggerImpl``.

        :param logger_impl: the logger implementations where all logging calls will be forwarded to.
        """
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


class BaseDirectStdAllLevelLogger(BaseStdProtocolAllLevelLogger, DirectStdAllLevelLogger, ABC):

    def __init__(self, logger_impl: BaseDirectStdAllLevelLoggerImpl,
                 level_name_map: dict[int, str] | None = None):
        """
        Implementation for a std protocol logger which provides all logging levels by the protocol implementation.

        see ``BaseDirectStdAllLevelLoggerImpl``.

        This class also registers the log-level->log-level-name if one is supplied. But doesn't do any
        level registration if log-level->log-level-name is empty or not supplied.

        ``DirectStdAllLevelLogger.register_levels()`` can be called to initialise and register default levels prior
        to creating this class's object.

        :param logger_impl: the logger implementations where all logging calls will be forwarded to.
        :param level_name_map: a log-level->log-level-name map. eg: ``30`` -> ``INFO``. This is useful for registering
            the level->name map with the logger.
        """
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


class DirectAllLevelLogger(BaseDirectStdAllLevelLogger, AllLevelLogger):

    def __init__(self, logger_impl: BaseDirectStdAllLevelLoggerImpl,
                 level_name_map: dict[int, str] | None = None):
        """
        Std protocol logger which provides all logging levels by the protocol implementation.

        see ``BaseDirectStdAllLevelLoggerImpl``.

        This class also registers the log-level->log-level-name if one is supplied. But doesn't do any
        level registration if log-level->log-level-name is empty or not supplied.

        ``DirectStdAllLevelLogger.register_levels()`` can be called to initialise and register default levels prior
        to creating this class's object.

        :param logger_impl: the logger implementations where all logging calls will be forwarded to.
        :param level_name_map: a log-level->log-level-name map. eg: ``30`` -> ``INFO``. This is useful for registering
            the level->name map with the logger.
        """
        super().__init__(logger_impl, level_name_map)

    @property
    def logger_impl(self) -> BaseDirectStdAllLevelLoggerImpl:
        return cast(BaseDirectStdAllLevelLoggerImpl, self._logger_impl)
