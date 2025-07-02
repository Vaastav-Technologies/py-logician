#!/usr/bin/env python3
# coding=utf-8

"""
Logging base interfaces are for implementation as well as extension.
"""

from abc import abstractmethod
from typing import Protocol


class LogLogProtocol(Protocol):
    """
    Protocol supporting the log method.
    """
    @abstractmethod
    def log(self, level: int, msg, *args, **kwargs) -> None:
        ...


class TraceLogProtocol(Protocol):
    """
    Protocol supporting the trace method.
    """
    @abstractmethod
    def trace(self, msg, *args, **kwargs) -> None:
        ...


class DebugLogProtocol(Protocol):
    """
    Protocol supporting the debug method.
    """
    @abstractmethod
    def debug(self, msg, *args, **kwargs) -> None:
        ...


class InfoLogProtocol(Protocol):
    """
    Protocol supporting the info method.
    """
    @abstractmethod
    def info(self, msg, *args, **kwargs) -> None:
        ...


class SuccessLogProtocol(Protocol):
    """
    Protocol supporting the success method.
    """
    @abstractmethod
    def success(self, msg, *args, **kwargs) -> None:
        pass


class NoticeLogProtocol(Protocol):
    """
    Protocol supporting the notice method.
    """
    @abstractmethod
    def notice(self, msg, *args, **kwargs) -> None:
        pass


class CommandLogProtocol(Protocol):
    """
    Protocol supporting the command logging. This can be used to log a command's stderr into the logger itself.
    """
    @abstractmethod
    def cmd(self, msg, cmd_name: str | None = None, *args, **kwargs) -> None:
        """
        Log a commands' captured output (maybe stderr or stdout)

        :param msg: The captured output.
        :param cmd_name: Which command name to register the command level to. If ``None`` then the default level-name
            is picked-up.
        """
        ...


class WarningLogProtocol(Protocol):
    """
    Protocol supporting the warning method.
    """
    @abstractmethod
    def warning(self, msg, *args, **kwargs) -> None:
        ...


class ErrorLogProtocol(Protocol):
    """
    Protocol supporting the error method.
    """
    @abstractmethod
    def error(self, msg, *args, **kwargs) -> None:
        ...


class ExceptionLogProtocol(Protocol):
    """
    Protocol supporting the exception method.
    """
    @abstractmethod
    def exception(self, msg, *args, **kwargs) -> None:
        pass


class CriticalLogProtocol(Protocol):
    """
    Protocol supporting the critical method.
    """
    @abstractmethod
    def critical(self, msg, *args, **kwargs) -> None:
        ...


class FatalLogProtocol(Protocol):
    """
    Protocol supporting the critical method.
    """
    @abstractmethod
    def fatal(self, msg, *args, **kwargs) -> None:
        pass


class _MinLogProtocol(LogLogProtocol, DebugLogProtocol, InfoLogProtocol, WarningLogProtocol, ErrorLogProtocol,
                      CriticalLogProtocol, Protocol):
    """
    This logger protocol is designed for extension but not direct implementation.

    Useful when ``is-a`` relationship cannot be established between the interfaces that have most of the methods of
    each-other but conceptually do not behave in an ``is-a`` relationship.

    e.g.::

        AllLogProtocol has all the methods of MinLogProtocol but conceptually AllLogProtocol cannot be put in place
        of MinLogProtocol, i.e. there is no is-a relationship between them.


    Logger that has all the basic logging levels common to most (nearly all) loggers, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL
    """
    pass


class MinLogProtocol(_MinLogProtocol, Protocol):
    """
    Logger protocol that has all the basic logging levels common to most (nearly all) loggers, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL
    """
    pass


class AllLogProtocol(TraceLogProtocol, _MinLogProtocol, SuccessLogProtocol, NoticeLogProtocol, CommandLogProtocol,
                     FatalLogProtocol, ExceptionLogProtocol, Protocol):
    """
    Logger protocol which supports all the common Logging levels, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    It also tries to add more levels that may facilitate users. Additionally supported log levels are::

        - TRACE
        - SUCCESS
        - NOTICE
        - COMMAND
        - FATAL
        - EXCEPTION
    """
    pass


class HasUnderlyingLogger(Protocol):
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
        interfaces with a particular implementation and this will hinder in swapping logger implementations.

        :return: the contained underlying logger.
        """
        pass


class AllLevelLogger(AllLogProtocol, HasUnderlyingLogger, Protocol):
    """
    Logger which supports all the common Logging levels, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    It also tries to add more levels that may facilitate users. Additionally supported log levels are::

        - TRACE
        - SUCCESS
        - NOTICE
        - COMMAND
        - FATAL
        - EXCEPTION

    And delegates the actual logging to an ``underlying_logger``, see ``HasUnderlyingLogger``.
    """
    pass
