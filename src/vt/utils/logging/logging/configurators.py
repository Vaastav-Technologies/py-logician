#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger configurators.
"""

import logging
from abc import abstractmethod
from typing import Protocol, Literal

from vt.utils.logging.logging.std_log.base import DirectStdAllLevelLogger
from vt.utils.logging.warnings import vt_warn


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


V_LITERAL = Literal['v', 'vv', 'vvv']
"""
Verbosity literal. Progressively denotes more and more verbosity.
"""
Q_LITERAL = Literal['q', 'qq', 'qqq']
"""
Quietness literal. Progressively denotes more and more quietness.
"""
type VQ_DICT_LITERAL[T] = dict[V_LITERAL | Q_LITERAL, T]
"""
Literal denoting how should a {``verbosity-quietness -> logging-level``} dict should be structured.
"""


class VQConfigurator[T](Protocol):
    @property
    @abstractmethod
    def vq_level_map(self) -> VQ_DICT_LITERAL[T]:
        ...

    @abstractmethod
    def validate(self, verbosity: V_LITERAL, quietness: Q_LITERAL) -> bool:
        ...

    @abstractmethod
    def get_effective_level(self, verbosity: V_LITERAL, quietness: Q_LITERAL, default_level: T | None = None) -> T:
        ...
