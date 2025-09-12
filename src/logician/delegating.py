#!/usr/bin/env python3
# coding=utf-8

"""
Loggers which are designed to delegate responsibility of logging to certain logging bridges.
"""

from abc import abstractmethod
from typing import Protocol

from logician import MinLogProtocol, AllLevelLogger
from logician.base import _MinLogProtocol


class ProtocolMinLevelLoggerImplBase[L](_MinLogProtocol[L], Protocol):
    """
    Bridge implementation base for extension in unrelated (non is-a relationship) loggers which support
    these operations::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL.

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass


class ProtocolMinLevelLoggerImplABC[L](
    ProtocolMinLevelLoggerImplBase[L], MinLogProtocol[L], Protocol
):
    """
    Bridge implementation base for extension by Min Log level loggers, i.e. loggers which support these operations::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass


class AllLevelLoggerImplABC[L](
    ProtocolMinLevelLoggerImplBase[L], AllLevelLogger[L], Protocol
):
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
        - COMMAND
        - FATAL
        - EXCEPTION

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass


class DelegatingLogger[L](Protocol):
    """
    A logger which delegates its logging capabilities to another logger implementation to facilitate a bridge.

    L - Level type, for e.g. ``int`` for python std logging.
    """

    @property
    @abstractmethod
    def logger_impl(self) -> ProtocolMinLevelLoggerImplBase[L]:
        """
        :return: the logging-class which implements logging capability.
        """
        pass
