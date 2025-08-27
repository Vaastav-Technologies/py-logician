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
at the time of logician logger configurator creation and hence client can configure the logger as they please before
supplying the logger class to perform delegation onto by this library.
"""


from logging import Logger


# region base re-exports
from logician.base import AllLevelLogger as AllLevelLogger
from logician.base import MinLogProtocol as MinLogProtocol
# endregion

# region std-log re-exports
from logician.std_log import StdLogProtocol as StdLogProtocol
from logician.std_log import StdLevelLogger as StdLevelLogger
from logician.std_log import StdProtocolAllLevelLogger as StdProtocolAllLevelLogger
from logician.std_log import BaseDirectStdAllLevelLogger as BaseDirectStdAllLevelLogger
from logician.std_log import DirectAllLevelLogger as DirectAllLevelLogger
from logician.std_log import DirectStdAllLevelLogger as DirectStdAllLevelLogger
# endregion

from logician.std_log.all_levels_impl import DirectAllLevelLoggerImpl as _DALImpl

from logician.constants import LGCN_ALL_LOG_ENV_VAR as LGCN_ALL_LOG_ENV_VAR

from logician.utils import command_or_file as command_or_file

from vt.utils.errors.error_specs import ErrorMsgFormer as ErrorMsgFormer

errmsg_creator = ErrorMsgFormer
"""
Create formatted error messages using this global instance.

To get a local instance use ``errmsg_creator.clone_with(...)``.
"""


def get_direct_all_level_logger(logger: Logger) -> DirectStdAllLevelLogger:
    return DirectAllLevelLogger(_DALImpl(logger))
