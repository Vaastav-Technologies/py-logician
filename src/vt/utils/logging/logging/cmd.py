#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for commands. These loggers implement all logger levels except CRITICAL is changed to FATAL.
"""
from typing import Protocol

from vt.utils.logging.logging.base import TraceLogProtocol, DebugLogProtocol, InfoLogProtocol, \
    WarningLogProtocol, FatalLogProtocol, LogLogProtocol, ErrorLogProtocol, SuccessLogProtocol, NoticeLogProtocol, \
    ExceptionLogProtocol, HasUnderlyingLogger


class MinCmdLogProtocol(LogLogProtocol, DebugLogProtocol, InfoLogProtocol, WarningLogProtocol, ErrorLogProtocol,
                        FatalLogProtocol, Protocol):
    """
    Interface for::

        - LOG
        - DEBUG
        - INFO
        - WARNING
        - ERROR
        - FATAL

    logging levels.
    """
    pass


class AllCmdLogProtocol(TraceLogProtocol, MinCmdLogProtocol, SuccessLogProtocol, NoticeLogProtocol,
                        ExceptionLogProtocol, Protocol):
    """
    Interface for::

        - All ``MinCmdLogProtocol`` log levels.
        - TRACE
        - SUCCESS
        - NOTICE
        - EXCEPTION

    logging levels.

    see ``MinCmdLogProtocol``.
    """
    pass


class AllLevelCmdLogger(AllCmdLogProtocol, HasUnderlyingLogger, Protocol):
    """
    Logger interface for::

        - All ``AllCmdLogProtocol`` log levels.

    logging levels.

    see ``AllCmdLogProtocol``.
    """
    pass
