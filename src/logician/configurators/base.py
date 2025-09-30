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

    # TODO: make this accept logger param based on a type param from LoggerConfigurator. This will make
    #  LoggerConfigurator configure different types of loggers with the same interface.
    #  The decision to directly accept a python std logger instead of a type param was made to simplify and fast-pace
    #  the POC.
    #  This can later be changed to make it into a resilient interface .
    @abstractmethod
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        """
        Configure the std python logger for various formatting quick-hands.

        :param logger: std python logger
        :return: A configured All level logging std python logger.
        """
        pass  # pragma: no cover

    @abstractmethod
    def clone(self, **overrides) -> "LoggerConfigurator":
        """
        :param overrides: overriding keyword args.
        :return: a new instance of the ``LoggerConfigurator`` with the provided overrides.
        """
        ...  # pragma: no cover


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
        ...  # pragma: no cover


class LevelTarget[L](Protocol):
    """
    Permits levels to be set.

    L - Level type, for e.g. ``int`` for python std logging.
    """

    @property
    @abstractmethod
    def level(self) -> L:
        """
        :return: current level.
        """
        ...  # pragma: no cover

    @abstractmethod
    def set_level(self, new_level: L) -> L:
        """
        Sets new level.

        :param new_level: sets to this level.
        :return: the old level.
        """
        ...  # pragma: no cover


class LevelLoggerConfigurator[L](LevelTarget[L], LoggerConfigurator, Protocol):
    """
    A logger configurator which allows setting levels from outside of it.

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass
