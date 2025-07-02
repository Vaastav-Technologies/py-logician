#!/usr/bin/env python3
# coding=utf-8

"""
All logging interface implementation by the standard logging library of python.

All level of logging are supported by these loggers using delegation and indirection
"""
from abc import ABC, abstractmethod
from logging import Logger
from typing import override, cast, Protocol

from logician import AllLevelLogger
from logician.delegating import DelegatingLogger
from logician.std_log import StdLogProtocol
from logician.std_log.base import DirectStdAllLevelLogger
from logician.std_log.all_levels_impl import StdProtocolAllLevelLoggerImpl, \
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

    @override
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
    def cmd(self, msg, cmd_name: str | None = None, *args, **kwargs) -> None:
        """
        Log a commands' captured output (maybe stderr or stdout)

        :param msg: The captured output.
        :param cmd_name: Which command name to register the command level to. If ``None`` then the default level-name
            ``COMMAND`` is picked-up. But as this is a ``DelegatingLogger`` hence this behavior can be altered in the
            delegatee class.
        """
        self.logger_impl.cmd(msg, cmd_name, *args, **kwargs)

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
                 level_name_map: dict[int, str] | None = None, cmd_name: str | None = None):
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
        :param cmd_name: level name for the command-log-level. ``None`` specifies that the default ``COMMAND`` will
            be shown on log.cmd() call. But as this is a ``DelegatingLogger`` hence this behavior can be altered in the
            delegatee class.
        """
        super().__init__(logger_impl)
        if level_name_map:
            BaseDirectStdAllLevelLogger.register_levels(level_name_map)
        self.level_name_map = level_name_map
        self.cmd_name = cmd_name

    @override
    @property
    def logger_impl(self) -> BaseDirectStdAllLevelLoggerImpl:
        return cast(BaseDirectStdAllLevelLoggerImpl, self._logger_impl)

    @override
    @property
    def underlying_logger(self) -> Logger: # noqa
        return cast(Logger, self._underlying_logger)

    @override
    def cmd(self, msg, cmd_name: str | None = None, *args, **kwargs) -> None:
        """
        Log a commands' captured output (maybe stderr or stdout)

        :param msg: The captured output.
        :param cmd_name: Which command name to register the command logging level to. If ``None`` then the ctor-supplied
            level-name ``self.cmd_name`` is picked-up. If ``self.cmd_name`` is also ``None`` then default
            ``COMMAND`` is picked-up. But as this is a ``DelegatingLogger`` hence this behavior can be altered in the
            delegatee class.
        """
        final_cmd_name = cmd_name or self.cmd_name
        self.logger_impl.cmd(msg, final_cmd_name, *args, **kwargs)


class DirectAllLevelLogger(BaseDirectStdAllLevelLogger, AllLevelLogger):

    def __init__(self, logger_impl: BaseDirectStdAllLevelLoggerImpl,
                 level_name_map: dict[int, str] | None = None, cmd_name: str | None = None):
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
        :param cmd_name: level name for the command-log-level. ``None`` specifies that the default ``COMMAND`` will
            be shown on log.cmd() call. But as this is a ``DelegatingLogger`` hence this behavior can be altered in the
            delegatee class.
        """
        super().__init__(logger_impl, level_name_map, cmd_name)

    @override
    @property
    def logger_impl(self) -> BaseDirectStdAllLevelLoggerImpl:
        return cast(BaseDirectStdAllLevelLoggerImpl, self._logger_impl)
