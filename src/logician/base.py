#!/usr/bin/env python3
# coding=utf-8

"""
Logging base interfaces are for implementation as well as extension.
"""

from abc import abstractmethod
from typing import Protocol


class LogLogProtocol[L](Protocol):
    """
    Protocol supporting the log method.

    L - Level type, for e.g. ``int`` for python std logging.
    """

    @abstractmethod
    def log(self, level: L, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class TraceLogProtocol(Protocol):
    """
    Protocol supporting the trace method.
    """

    @abstractmethod
    def trace(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class DebugLogProtocol(Protocol):
    """
    Protocol supporting the debug method.
    """

    @abstractmethod
    def debug(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class InfoLogProtocol(Protocol):
    """
    Protocol supporting the info method.
    """

    @abstractmethod
    def info(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class SuccessLogProtocol(Protocol):
    """
    Protocol supporting the success method.
    """

    @abstractmethod
    def success(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class NoticeLogProtocol(Protocol):
    """
    Protocol supporting the notice method.
    """

    @abstractmethod
    def notice(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


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
        ...  # pragma: no cover


class WarningLogProtocol(Protocol):
    """
    Protocol supporting the warning method.
    """

    @abstractmethod
    def warning(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class ErrorLogProtocol(Protocol):
    """
    Protocol supporting the error method.
    """

    @abstractmethod
    def error(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class ExceptionLogProtocol(Protocol):
    """
    Protocol supporting the exception method.
    """

    @abstractmethod
    def exception(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class CriticalLogProtocol(Protocol):
    """
    Protocol supporting the critical method.
    """

    @abstractmethod
    def critical(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class FatalLogProtocol(Protocol):
    """
    Protocol supporting the critical method.
    """

    @abstractmethod
    def fatal(self, msg, *args, **kwargs) -> None: ...  # pragma: no cover


class _MinLogProtocol[L](
    LogLogProtocol[L],
    DebugLogProtocol,
    InfoLogProtocol,
    WarningLogProtocol,
    ErrorLogProtocol,
    CriticalLogProtocol,
    Protocol,
):
    """
    This logger protocol is designed for extension but not direct implementation.

    Useful when ``is-a`` relationship cannot be established between the interfaces that have most of the methods of
    each-other but conceptually do not behave in an ``is-a`` relationship.

    L - Level type, for e.g. ``int`` for python std logging.

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


class MinLogProtocol[L](_MinLogProtocol[L], Protocol):
    """
    Logger protocol that has all the basic logging levels common to most (nearly all) loggers, i.e.::

        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - CRITICAL

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass


class AllLogProtocol[L](
    TraceLogProtocol,
    _MinLogProtocol[L],
    SuccessLogProtocol,
    NoticeLogProtocol,
    CommandLogProtocol,
    FatalLogProtocol,
    ExceptionLogProtocol,
    Protocol,
):
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

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass


class HasUnderlyingLogger[L](Protocol):
    """
    Insists that an underlying logger is contained in the class implementing this interface.

    Can return the contained underlying logger for the client class to perform actions in the future if needed.

    L - Level type, for e.g. ``int`` for python std logging.
    """

    @property
    @abstractmethod
    def underlying_logger(self) -> MinLogProtocol[L]:
        """
        It may not be a good idea to directly call this method to obtain underlying logger after class is
        initialised and its use is started. That is the case because that obtained underlying logger may tie the
        interfaces with a particular implementation and this will hinder in swapping logger implementations.

        :return: the contained underlying logger.
        """
        pass  # pragma: no cover


class SupportsTraceback(Protocol):
    """
    Can process (in most cases, log) the exception tracebacks.
    """

    @property
    @abstractmethod
    def traceback_enabled(self) -> bool:
        """
        :return: whether the traceback processing (in most cases, logging) is enabled.
        """
        ...


class AllLevelLogger[L](
    AllLogProtocol[L], HasUnderlyingLogger[L], SupportsTraceback, Protocol
):
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

    L - Level type, for e.g. ``int`` for python std logging.
    """

    pass
