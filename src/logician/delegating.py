#!/usr/bin/env python3
# coding=utf-8

"""
Loggers which are designed to delegate responsibility of logging to certain logging bridges.
"""

from abc import abstractmethod
from typing import Protocol

from logician import MinLogProtocol, AllLevelLogger
from logician.base import _MinLogProtocol


class ProtocolMinLevelLoggerImplBase(_MinLogProtocol, Protocol):
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


class ProtocolMinLevelLoggerImplABC(ProtocolMinLevelLoggerImplBase, MinLogProtocol, Protocol):
    """
    Bridge implementation base for extension by Min Log level loggers, i.e. loggers which support these operations::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL
    """
    pass


class AllLevelLoggerImplABC(ProtocolMinLevelLoggerImplBase, AllLevelLogger, Protocol):
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
    """
    pass


class DelegatingLogger(Protocol):
    """
    A logger which delegates its logging capabilities to another logger implementation to facilitate a bridge.
    """
    @property
    @abstractmethod
    def logger_impl(self) -> ProtocolMinLevelLoggerImplBase:
        """
        :return: the logging-class which implements logging capability.
        """
        pass
