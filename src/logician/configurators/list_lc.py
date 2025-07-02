#!/usr/bin/env python3
# coding=utf-8


"""
Configure loggers as per level supplied by a list.

First non-None level in this supplied list is picked up by default.
"""
import logging
from typing import override

from logician import DirectStdAllLevelLogger
from logician.configurators import LoggerConfigurator, HasUnderlyingConfigurator, \
    LevelLoggerConfigurator
from logician.std_log.utils import get_first_non_none


class ListLoggerConfigurator[T](LoggerConfigurator, HasUnderlyingConfigurator):
    DEFAULT_LEVEL_PICKUP_FIRST_NON_NONE = get_first_non_none

    def __init__(self, level_list: list[T | None], configurator: LevelLoggerConfigurator[T],
                 level_pickup_strategy=DEFAULT_LEVEL_PICKUP_FIRST_NON_NONE):
        """
        Picks up the first non ``None`` level from the supplied ``level_list`` to configure the logger underneath.

        * Examples:

          * supplied ``level_list`` cannot be ``None``:

            >>> ListLoggerConfigurator(None, # noqa: as level_list is deliberately passed as None
            ...     None) # noqa: as configurator is unused and passed as None
            Traceback (most recent call last):
            ValueError: Level list must not be None.

        :param level_list: list of log levels which may contain ``None``. First non-``None`` value
            is picked-up by default for logger configuration.
        :param configurator: configurator which is decorated by this logger-configurator.
        :param level_pickup_strategy: pick up a level from the list of levels supplied in ``level_list``. Default is
            to pick up the first non-``None`` level. ``DEFAULT_LEVEL_PICKUP_FIRST_NON_NONE``.
        """
        if level_list is None:
            raise ValueError("Level list must not be None.")
        self._level_list = level_list
        self.configurator = configurator
        self.level_pickup_strategy = level_pickup_strategy

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        final_level = self.level_pickup_strategy(self.level_list, self.underlying_configurator.level)
        self.underlying_configurator.set_level(final_level)
        return self.underlying_configurator.configure(logger)

    @override
    @property
    def underlying_configurator(self) -> LevelLoggerConfigurator[T]:
        return self.configurator

    @property
    def level_list(self) -> list[T | None]:
        return self._level_list

    @override
    def clone_with(self, **kwargs) -> 'ListLoggerConfigurator[T]':
        """
        kwargs:
            ``level_list`` - list of log levels which may contain ``None``. First non-``None`` value is picked-up by
            default for logger configuration.

            ``configurator`` - configurator which is decorated by this logger-configurator.

            ``level_pickup_strategy`` - pick up a level from the list of levels supplied in ``level_list``.
            Default is to pick up the first non-``None`` level. ``DEFAULT_LEVEL_PICKUP_FIRST_NON_NONE``.
        :return: a new ``ListLoggerConfigurator``.
        """
        level_list = kwargs.pop('level_list', self.level_list.copy())
        configurator = kwargs.pop('configurator', self.configurator)
        level_pickup_strategy = kwargs.pop('level_pickup_strategy', self.level_pickup_strategy)
        return ListLoggerConfigurator[T](level_list, configurator, level_pickup_strategy)
