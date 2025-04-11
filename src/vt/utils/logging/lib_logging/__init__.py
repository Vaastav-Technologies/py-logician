#!/usr/bin/env python3
# coding=utf-8

"""
Logging related library.

This library is built to let other logging projects extend it and implement their own versions of various log levels.
Only log levels are of essence in this library as most of the logging concerns log levels and not the actual logger
setup.

Aim is to let users extend this library to fit their various log levels and logging goals and not think twice before
replacing one logger implementation with another.

Extending libraries are to be designed thinking that the underlying logger will be supplied by the client/caller
at the time of vt.utils.logging.logger creation and hence client can configure the logger as they please before
supplying the logger class to perform delegation onto by this library.
"""


from logging import Logger


from vt.utils.logging.lib_logging.base import AllLevelLogger, MinLogProtocol
from vt.utils.logging.lib_logging.std_log import StdLogProtocol, StdLevelLogger, StdProtocolAllLevelLogger, \
    BaseDirectStdAllLevelLogger, DirectAllLevelLogger, DirectStdAllLevelLogger
from vt.utils.logging.lib_logging.std_log.all_levels_impl import DirectAllLevelLoggerImpl as _DALImpl


def get_direct_all_level_logger(logger: Logger) -> DirectStdAllLevelLogger:
    return DirectAllLevelLogger(_DALImpl(logger))
