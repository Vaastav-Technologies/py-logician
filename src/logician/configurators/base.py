#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger configurators.
"""
import logging
from abc import abstractmethod
from typing import Protocol

from logician import DirectStdAllLevelLogger


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

    @abstractmethod
    def clone_with(self, **kwargs) -> 'LoggerConfigurator':
        """
        :param kwargs: overriding keyword args.
        :return: a new instance of the ``LoggerConfigurator`` with the provided overrides.
        """
        ...


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

    @property
    @abstractmethod
    def level(self) -> T:
        """
        :return: current level.
        """
        ...

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
