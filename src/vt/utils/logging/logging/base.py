#!/usr/bin/env python3
# coding=utf-8

"""
Logging base interfaces are for implementation as well as extension.
"""

from abc import ABC, abstractmethod
from typing import Protocol


class LogLogProtocol(Protocol):
    """
    Protocol supporting the log method.
    """
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        ...


class DebugLogProtocol(Protocol):
    """
    Protocol supporting the debug method.
    """
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...


class InfoLogProtocol(Protocol):
    """
    Protocol supporting the info method.
    """
    def info(self, msg: str, *args, **kwargs) -> None:
        ...


class WarningLogProtocol(Protocol):
    """
    Protocol supporting the warning method.
    """
    def warning(self, msg: str, *args, **kwargs) -> None:
        ...


class ErrorLogProtocol(Protocol):
    """
    Protocol supporting the error method.
    """
    def error(self, msg: str, *args, **kwargs) -> None:
        ...


class CriticalLogProtocol(Protocol):
    """
    Protocol supporting the critical method.
    """
    def critical(self, msg: str, *args, **kwargs) -> None:
        ...


class MinLogProtocol(LogLogProtocol, DebugLogProtocol, InfoLogProtocol, WarningLogProtocol, ErrorLogProtocol,
                     CriticalLogProtocol, Protocol):
    """
    Protocol denoting the minimum logging levels that most (nearly all) of the logger implementations provide.
    """
    pass


class HasUnderlyingLogger(ABC):
    """
    Insists that an underlying logger is contained in the class implementing this interface.

    Can return the contained underlying logger for the client class to perform actions in the future if needed.
    """
    @property
    @abstractmethod
    def underlying_logger(self) -> MinLogProtocol:
        """
        It may not be a good idea to directly call this method to obtain underlying logger after class is
        initialised and its use is started. That is the case because that obtained underlying logger may tie the
        interfaces with a particular implementation and thi will hinder in swapping logger implementations.

        :return: the contained underlying logger.
        """
        pass


class LogLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the log method.
    """
    @abstractmethod
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        pass


class TraceLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the trace method.
    """
    @abstractmethod
    def trace(self, msg, *args, **kwargs) -> None:
        pass


class DebugLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the debug method.
    """
    @abstractmethod
    def debug(self, msg, *args, **kwargs) -> None:
        pass


class InfoLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the info method.
    """
    @abstractmethod
    def info(self, msg, *args, **kwargs) -> None:
        pass


class SuccessLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the success method.
    """
    @abstractmethod
    def success(self, msg, *args, **kwargs) -> None:
        pass


class NoticeLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the notice method.
    """
    @abstractmethod
    def notice(self, msg, *args, **kwargs) -> None:
        pass


class WarningLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the warning method.
    """
    @abstractmethod
    def warning(self, msg, *args, **kwargs) -> None:
        pass


class ExceptionLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the exception method.
    """
    @abstractmethod
    def exception(self, msg, *args, **kwargs) -> None:
        pass


class ErrorLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the error method.
    """
    @abstractmethod
    def error(self, msg, *args, **kwargs) -> None:
        pass


class CriticalLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the critical method.
    """
    @abstractmethod
    def critical(self, msg, *args, **kwargs) -> None:
        pass


class FatalLevelLogger(HasUnderlyingLogger):
    """
    Logger that has the fatal method.
    """
    @abstractmethod
    def fatal(self, msg, *args, **kwargs) -> None:
        pass


class _MinLevelLogger(LogLevelLogger, DebugLevelLogger, InfoLevelLogger, WarningLevelLogger, ErrorLevelLogger,
                      CriticalLevelLogger, HasUnderlyingLogger, ABC):
    """
    This logger interface is designed for extension but not direct implementation.

    Useful when ``is-a`` relationship cannot be established between the interfaces that have most of the methods of
    each-other but conceptually do not behave in an ``is-a`` relationship.

    e.g.::

        AllLevelLogger has all the methods of MinLevelLogger but conceptually AllLevelLogger cannot be put in place
        of MinLevelLogger, i.e. there is no is-a relationship between them.
    """
    pass


class MinLevelLogger(_MinLevelLogger, ABC):
    """
    Logger that has all the basic logging levels common to most (nearly all) loggers, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL
    """
    pass


class AllLevelLogger(TraceLevelLogger, _MinLevelLogger, SuccessLevelLogger, NoticeLevelLogger, FatalLevelLogger,
                     ExceptionLevelLogger, ABC):
    """
    Logger which supports all the common Logging levels, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    It also tries to add more levels that may facilitate users, additional log levels are::

        - SUCCESS
        - NOTICE
        - FATAL
        - EXCEPTION
    """
    pass
