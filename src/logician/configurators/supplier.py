#!/usr/bin/env python3
# coding=utf-8


"""
Configure loggers as per level supplied by a supplier.
"""

import logging
from typing import Callable, override

from logician import DirectStdAllLevelLogger
from logician._repo import get_repo
from logician.configurators import (
    LoggerConfigurator,
    HasUnderlyingConfigurator,
    LevelLoggerConfigurator,
)


class SupplierLoggerConfigurator[T](LoggerConfigurator, HasUnderlyingConfigurator):
    def __init__(
        self,
        level_supplier: Callable[[], T | None],
        configurator: LevelLoggerConfigurator[T],
    ):
        """
        Configurator that configures loggers as per the level supplied by the ``level_supplier``.

        Examples:

        >>> from logician.stdlog.configurator import StdLoggerConfigurator

          * Typed:

            >>> _ = SupplierLoggerConfigurator[int](lambda: logging.DEBUG, StdLoggerConfigurator())

          * Untyped

            >>> _ = SupplierLoggerConfigurator(lambda : logging.INFO, StdLoggerConfigurator())

        :param level_supplier: a supplier to supply level.
        :param configurator: underlying configurator.
        """
        self.level_supplier = level_supplier
        self._underlying_configurator = configurator
        get_repo().init()

    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        """
        >>> from logician.stdlog.configurator import StdLoggerConfigurator
        >>> from logician.stdlog import NOTICE_LOG_LEVEL

        Examples:

          * Level set by the supplier: ``INFO`` level

            >>> _lgr = logging.getLogger("supplier-logger-demo-1")
            >>> lc = SupplierLoggerConfigurator(lambda : logging.INFO, StdLoggerConfigurator())
            >>> lgr = lc.configure(_lgr)
            >>> assert lgr.underlying_logger.level == logging.INFO

          * Supplier returns ``None`` hence, level is determined by the underlying configurator: ``NOTICE`` level

            >>> _lgr = logging.getLogger("supplier-logger-demo-2")
            >>> lc = StdLoggerConfigurator(level=NOTICE_LOG_LEVEL)
            >>> assert lc.level == NOTICE_LOG_LEVEL
            >>> lc = SupplierLoggerConfigurator(lambda : None, lc)
            >>> lgr = lc.configure(_lgr)
            >>> assert lgr.underlying_logger.level == NOTICE_LOG_LEVEL

        :param logger: the logger to configure.
        :return: configured logger with its logging level set by the ``level_supplier``.
        """
        computed_level = self.level_supplier()
        final_level = (
            computed_level
            if computed_level is not None
            else self.underlying_configurator.level
        )
        self.underlying_configurator.set_level(final_level)
        get_repo().index(logger.name, level=final_level)
        return self.underlying_configurator.configure(logger)

    @override
    @property
    def underlying_configurator(self) -> LevelLoggerConfigurator[T]:
        return self._underlying_configurator  # pragma: no cover

    @override
    def clone(self, **overrides) -> "SupplierLoggerConfigurator":
        """
        overrides:
            ``level_supplier`` - a supplier to supply level.

            ``configurator`` - underlying configurator.

        Examples:

        >>> import logging
        >>> from logician.stdlog.configurator import StdLoggerConfigurator

          * Simple clone, no overrides:

            >>> lc1 = SupplierLoggerConfigurator(lambda : logging.INFO, StdLoggerConfigurator())
            >>> lc2 = lc1.clone()
            >>> assert lc1.underlying_configurator == lc2.underlying_configurator and lc1.level_supplier == lc2.level_supplier

          * Clone, override just ``level_supplier``:

            >>> lc1 = SupplierLoggerConfigurator(lambda : logging.INFO, StdLoggerConfigurator())
            >>> lc2 = lc1.clone(level_supplier=lambda : logging.DEBUG)
            >>> assert lc1.underlying_configurator == lc2.underlying_configurator and lc1.level_supplier != lc2.level_supplier

          * Clone, override just ``configurator``:

            >>> lc1 = SupplierLoggerConfigurator(lambda : logging.INFO, StdLoggerConfigurator())
            >>> lc2 = lc1.clone(configurator=StdLoggerConfigurator(level=logging.CRITICAL))
            >>> assert lc1.underlying_configurator != lc2.underlying_configurator and lc1.level_supplier == lc2.level_supplier

          * Clone, override all:

            >>> lc1 = SupplierLoggerConfigurator(lambda : None, StdLoggerConfigurator())
            >>> lc2 = lc1.clone(level_supplier=lambda : logging.WARNING, configurator=StdLoggerConfigurator(level=logging.CRITICAL))
            >>> assert lc1.underlying_configurator != lc2.underlying_configurator and lc1.level_supplier != lc2.level_supplier

        :return: a new ``SupplierLoggerConfigurator``.
        """
        level_supplier = overrides.pop("level_supplier", self.level_supplier)
        configurator = overrides.pop("configurator", self.underlying_configurator)
        return SupplierLoggerConfigurator(level_supplier, configurator)
