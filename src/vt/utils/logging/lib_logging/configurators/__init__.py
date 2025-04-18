#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger configurators.
"""
import logging
import os
from abc import abstractmethod
from typing import Protocol, Callable, override

from vt.utils.logging.lib_logging import VT_ALL_LOG_ENV_VAR
from vt.utils.logging.lib_logging.std_log.base import DirectStdAllLevelLogger
from vt.utils.logging.lib_logging.std_log.utils import get_first_non_none


class LoggerConfigurator(Protocol):
    """
    Stores configuration information to configure the std python logger.
    """

    @abstractmethod
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        """
        Configure the std python logger for various formatting quick-hands.

        :param logger: std python logger
        :return: A configured All level logging std python logger.
        """
        pass


class HasUnderlyingConfigurator(Protocol):
    """
    A configurator which has other configurators underneath it. Majorly used to decorate configurators to add
    functionalities to them.
    """

    @property
    @abstractmethod
    def underlying_configurator(self) -> LoggerConfigurator:
        """
        :return: The underlying logger configurator which is decorated by this configurator.
        """
        ...


class LevelTarget[T](Protocol):
    """
    Permits levels to be set.
    """

    @abstractmethod
    def set_level(self, new_level: T) -> T:
        """
        Sets new level.

        :param new_level: sets to this level.
        :return: the old level.
        """
        ...


class LevelLoggerConfigurator[T](LevelTarget[T], LoggerConfigurator, Protocol):
    """
    A logger configurator which allows setting levels from outside of it.
    """
    pass


class SupplierLoggerConfigurator[T](LoggerConfigurator, HasUnderlyingConfigurator):

    def __init__(self, level_supplier: Callable[[], T], configurator: LevelLoggerConfigurator[T]):
        """
        Configurator that configures loggers as per the level supplied by the ``level_supplier``.

        :param level_supplier: a supplier to supply level.
        :param configurator: underlying configurator.
        """
        self.level_supplier = level_supplier
        self.configurator = configurator

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        final_level = self.level_supplier()
        self.configurator.set_level(final_level)
        return self.configurator.configure(logger)

    @override
    @property
    def underlying_configurator(self) -> LoggerConfigurator:
        return self.configurator


class ListLoggerConfigurator[T](LoggerConfigurator, HasUnderlyingConfigurator):

    def __init__(self, level_list: list[T | None], configurator: LevelLoggerConfigurator,
                 level_pickup_strategy =get_first_non_none):
        """
        Picks up the first non ``None`` level from the ``level_list`` to configure the logger underneath.

        :param level_list: list of log levels which may contain ``None``. First non-``None`` value
            is picked-up by default for logger configuration.
        :param configurator: configurator which is decorated by this logger-configurator.
        :param level_pickup_strategy: pick up a level from the list of levels supplied in ``level_list``. Default is
            to pick up the first non-``None`` level.
        """
        if not level_list:
            raise ValueError("Level list must not be None or empty.")
        self.level_list = level_list
        self.configurator = configurator
        self.level_pickup_strategy = level_pickup_strategy

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        final_level = self.level_pickup_strategy(self.level_list)
        if final_level:
            self.configurator.set_level(final_level)
        return self.configurator.configure(logger)

    @override
    @property
    def underlying_configurator(self) -> LoggerConfigurator:
        return self.configurator


class EnvListLC[T](ListLoggerConfigurator):
    def __init__(self, env_list: list[str], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy =get_first_non_none):
        """
        This logger configurator can be used to configure log level using values supplied from environment variables.
        Default behavior is to pick up the first passed environment variable value. Designed to process log level from
        multiple environment variables and hence has a precedence order to the values form environment variables. The
        first environment variable value takes highest precedence and then the precedence diminishes.

        :param env_list: list of environment variables. Default behavior is to take precedence in decreasing order.
        :param configurator: underlying logger configurator.
        :param level_pickup_strategy: strategy to pick-up level from a supplied list of levels. Default is to pick up
            the first supplied, then next and then so on.
        """
        super().__init__([os.getenv(e) for e in env_list], configurator, level_pickup_strategy)
        self._env_list = env_list

    def get_env_list(self):
        return self._env_list


class VTEnvListLC[T](EnvListLC[T]):
    def __init__(self, env_list: list[str], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy=get_first_non_none):
        """
        This logger configurator can be used to configure log level using values supplied from environment variables.
        Default behavior is to pick up the first passed environment variable value. Designed to process log level from
        multiple environment variables and hence has a precedence order to the values form environment variables. The
        first environment variable value takes highest precedence and then the precedence diminishes. Environment
        variable ``VT_ALL_LOG`` is always appended to ``env_list`` so that if no environment variable is registered
        then at least this one is registered.

        :param env_list: list of environment variables. Default behavior is to take precedence in decreasing order.
        :param configurator: underlying logger configurator.
        :param level_pickup_strategy: strategy to pick-up level from a supplied list of levels. Default is to pick up
            the first supplied, then next and then so on.
        """
        env_list.append(VT_ALL_LOG_ENV_VAR)
        super().__init__(env_list, configurator, level_pickup_strategy)
