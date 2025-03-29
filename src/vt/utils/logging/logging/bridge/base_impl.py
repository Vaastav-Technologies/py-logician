#!/usr/bin/env python3
# coding=utf-8

"""
Classes w.r.t implementation inheritance for base logger are defined here.
"""

from abc import ABC, abstractmethod
from typing import override

from vt.utils.logging.logging import MinLevelLogger, AllLevelLogger
from vt.utils.logging.logging.base import _MinLevelLogger


class _ProtocolMinLevelLoggerImplBase(_MinLevelLogger, ABC):
    """
    Bridge implementation base for extension in unrelated (non is-a relationship) loggers which support
    these operations::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL.
    """
    pass


class ProtocolMinLevelLoggerImplABC(_ProtocolMinLevelLoggerImplBase, MinLevelLogger, ABC):
    """
    Bridge implementation base for extension by Min Log level loggers, i.e. loggers which support these operations::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL
    """
    pass


class AllLevelLoggerImplABC(_ProtocolMinLevelLoggerImplBase, AllLevelLogger, ABC):
    """
    Bridge implementation base for extension by loggers which supports all the common Logging levels, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    It also tries to add more levels that may facilitate users, additional log levels are::

        - TRACE
        - SUCCESS
        - NOTICE
        - FATAL
        - EXCEPTION
    """
    pass


class BaseDelegatingLogger(_MinLevelLogger, ABC):
    @property
    @abstractmethod
    def logger_impl(self) -> _ProtocolMinLevelLoggerImplBase:
        pass


class DelegatingProtocolMinLevelLogger(BaseDelegatingLogger, MinLevelLogger, ABC):
    @property
    @abstractmethod
    @override
    def logger_impl(self) -> _ProtocolMinLevelLoggerImplBase:
        pass


class DelegatingAllLevelLogger(BaseDelegatingLogger, AllLevelLogger, ABC):
    @property
    @abstractmethod
    @override
    def logger_impl(self) -> AllLevelLoggerImplABC:
        pass
