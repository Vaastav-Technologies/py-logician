#!/usr/bin/env python3
# coding=utf-8

"""
Logging base interfaces are defined.
"""

from abc import ABC, abstractmethod
from typing import Protocol


class LogLogProtocol(Protocol):
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        ...


class DebugLogProtocol(Protocol):
    def debug(self, msg: str, *args, **kwargs) -> None:
        ...


class InfoLogProtocol(Protocol):
    def info(self, msg: str, *args, **kwargs) -> None:
        ...


class WarningLogProtocol(Protocol):
    def warning(self, msg: str, *args, **kwargs) -> None:
        ...


class ErrorLogProtocol(Protocol):
    def error(self, msg: str, *args, **kwargs) -> None:
        ...


class CriticalLogProtocol(Protocol):
    def critical(self, msg: str, *args, **kwargs) -> None:
        ...


class StdLogProtocol(LogLogProtocol, DebugLogProtocol, InfoLogProtocol, WarningLogProtocol, ErrorLogProtocol,
                     CriticalLogProtocol, Protocol):
    pass


class HasUnderlyingLogger(ABC):
    @property
    @abstractmethod
    def underlying_logger(self) -> StdLogProtocol:
        pass


class LogLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def log(self, level: int, msg: str, *args, **kwargs) -> None:
        pass


class TraceLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def trace(self, msg, *args, **kwargs) -> None:
        pass


class DebugLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def debug(self, msg, *args, **kwargs) -> None:
        pass


class InfoLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def info(self, msg, *args, **kwargs) -> None:
        pass


class SuccessLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def success(self, msg, *args, **kwargs) -> None:
        pass


class NoticeLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def notice(self, msg, *args, **kwargs) -> None:
        pass


class WarningLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def warning(self, msg, *args, **kwargs) -> None:
        pass


class ExceptionLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def exception(self, msg, *args, **kwargs) -> None:
        pass


class ErrorLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def error(self, msg, *args, **kwargs) -> None:
        pass


class CriticalLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def critical(self, msg, *args, **kwargs) -> None:
        pass


class FatalLevelLogger(HasUnderlyingLogger):
    @abstractmethod
    def fatal(self, msg, *args, **kwargs) -> None:
        pass


class MinLevelLogger(DebugLevelLogger, InfoLevelLogger, WarningLevelLogger, ErrorLevelLogger, CriticalLevelLogger,
                     ExceptionLevelLogger, LogLevelLogger, HasUnderlyingLogger, ABC):
    pass


class AllLevelLogger(TraceLevelLogger, DebugLevelLogger, InfoLevelLogger, SuccessLevelLogger, NoticeLevelLogger,
                     WarningLevelLogger, ErrorLevelLogger, CriticalLevelLogger, FatalLevelLogger, ExceptionLevelLogger,
                     LogLevelLogger, HasUnderlyingLogger, ABC):
    pass
