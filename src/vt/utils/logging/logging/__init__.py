#!/usr/bin/env python3
# coding=utf-8

"""
Logging related library.

This library is built to let other logging projects extent it and implement their own versions of various log levels.
Only log levels are of essence in this library as most of the logging concerns log levels and not the actual logger
setup.

Aim is to let users extend this library to fit their various log levels and logging goals and not think twice before
replacing one logger implementation with another.

Extending libraries are to be designed thinking that the underlying logger will be supplied by the client/caller
at the time of vt.utils.logging.logger creation and hence client can configure the logger as they please before
supplying the logger class to perform delegation onto by this library.
"""


from logging import Logger


from vt.utils.logging.logging.base import MinLevelLogger, AllLevelLogger, MinLogProtocol
from vt.utils.logging.logging.std_log import StdLogProtocol, StdLevelLogger, ProtocolStdLevelLogger, \
    BaseDirectStdLevelLogger, BaseDirectAllLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import DirectAllLevelLoggerImpl as _DALImpl


def get_direct_all_level_logger(logger: Logger) -> BaseDirectAllLevelLogger:
    return BaseDirectAllLevelLogger(_DALImpl(logger))
