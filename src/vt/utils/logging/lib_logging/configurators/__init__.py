#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger configurators.
"""
import logging
import os
from abc import abstractmethod
from typing import Protocol, Callable

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


class SupplierLoggerConfigurator[T](LoggerConfigurator):
    def __init__(self, level_supplier: Callable[[], T], configurator: LevelLoggerConfigurator[T]):
        self.level_supplier = level_supplier
        self.configurator = configurator

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        final_level = self.level_supplier()
        self.configurator.set_level(final_level)
        return self.configurator.configure(logger)


class ListLoggerConfigurator[T](LoggerConfigurator):

    def __init__(self, level_list: list[T], configurator: LevelLoggerConfigurator,
                 level_pickup_strategy =get_first_non_none):
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


class EnvListLC[T](ListLoggerConfigurator):
    def __init__(self, env_list: list[str], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy =get_first_non_none):
        super().__init__([os.getenv(e) for e in env_list], configurator, level_pickup_strategy)
        self._env_list = env_list

    def get_env_list(self):
        return self._env_list


class VTEnvListLC[T](EnvListLC[T]):
    def __init__(self, env_list: list[str], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy=get_first_non_none):
        env_list.append(VT_ALL_LOG_ENV_VAR)
        super().__init__(env_list, configurator, level_pickup_strategy)
