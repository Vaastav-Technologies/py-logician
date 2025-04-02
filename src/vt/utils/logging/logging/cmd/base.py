#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for commands. These loggers implement all logger levels except CRITICAL is changed to FATAL.
"""
from typing import Protocol

from vt.utils.logging.logging.base import TraceLogProtocol, DebugLogProtocol, InfoLogProtocol, \
    WarningLogProtocol, FatalLogProtocol, LogLogProtocol, ErrorLogProtocol, SuccessLogProtocol, NoticeLogProtocol, \
    ExceptionLogProtocol


class MinCmdLogProtocol(LogLogProtocol, DebugLogProtocol, InfoLogProtocol, WarningLogProtocol, ErrorLogProtocol,
                        FatalLogProtocol, Protocol):
    pass


class AllCmdLogProtocol(TraceLogProtocol, MinCmdLogProtocol, SuccessLogProtocol, NoticeLogProtocol,
                        ExceptionLogProtocol, Protocol):
    pass
