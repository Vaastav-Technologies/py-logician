#!/usr/bin/env python3
# coding=utf-8


"""
Configure loggers as per level supplied by a supplier.
"""
import logging
from typing import Callable, override

from logician import DirectStdAllLevelLogger
from logician.configurators import LoggerConfigurator, HasUnderlyingConfigurator, \
    LevelLoggerConfigurator


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
        computed_level = self.level_supplier()
        final_level = computed_level if computed_level is not None else self.underlying_configurator.level
        self.underlying_configurator.set_level(final_level)
        return self.underlying_configurator.configure(logger)

    @override
    @property
    def underlying_configurator(self) -> LevelLoggerConfigurator[T]:
        return self.configurator

    @override
    def clone_with(self, **kwargs) -> 'SupplierLoggerConfigurator':
        """
        kwargs:
            ``level_supplier`` - a supplier to supply level.

            ``configurator`` - underlying configurator.
        :return: a new ``SupplierLoggerConfigurator``.
        """
        level_supplier = kwargs.pop('level_supplier', self.level_supplier)
        configurator = kwargs.pop('configurator', self.configurator)
        return SupplierLoggerConfigurator(level_supplier, configurator)
