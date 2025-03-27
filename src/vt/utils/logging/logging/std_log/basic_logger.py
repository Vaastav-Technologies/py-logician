#!/usr/bin/env python3
# coding=utf-8

"""
Basic logging interface implementation by the standard logging library of python.

Basic loggers only support operations::

    - log
    - debug
    - info
    - warning
    - error
    - exception
    - critical
    - fatal
"""
from logging import Logger
from typing import override, cast

from vt.utils.logging.logging.std_log import StdLogProtocol
from vt.utils.logging.logging.std_log.basic_logger_impl import BaseStdLevelLoggerImpl


class ProtocolStdLevelLogger(BaseStdLevelLoggerImpl): # implementation inheritance, not is-a

    def __init__(self, underlying_logger: StdLogProtocol):
        """
        Logger that implements all the logging levels of python standard logging PROTOCOL and simply delegates
        method calls to the underlying logger.

        :param underlying_logger: logger (python standard logger logging PROTOCOL) that actually performs the logging.
        """
        super().__init__(underlying_logger)


class DirectStdLevelLogger(BaseStdLevelLoggerImpl): # implementation inheritance, not is-a

    def __init__(self, underlying_logger: Logger):
        """
        Logger that implements all the logging levels of python standard logging DIRECTLY. It simply delegates method
        calls to the underlying logger.

        :param underlying_logger: logger (actual python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger) # noqa

    @override
    @property
    def underlying_logger(self) -> Logger:
        return cast(Logger, self._underlying_logger)
