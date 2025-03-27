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
from vt.utils.logging.logging.std_log._base_impl import _BaseStdLevelLogger


class BasicStdProtocolLevelLogger(_BaseStdLevelLogger): # implementation inheritance, not is-a

    def __init__(self, underlying_logger: StdLogProtocol):
        """
        Basic logger that implements all the logging levels of python standard logging protocol and simply delegates
        method calls to the underlying logger.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger)


class BasicStdLevelLogger(_BaseStdLevelLogger): # implementation inheritance, not is-a

    def __init__(self, underlying_logger: Logger):
        """
        Basic logger that implements all the logging levels of python standard logging and simply delegates method
        calls to the underlying logger.

        :param underlying_logger: logger (python standard logger) that actually performs the logging.
        """
        super().__init__(underlying_logger) # noqa

    @override
    @property
    def underlying_logger(self) -> Logger:
        return cast(Logger, self._underlying_logger)
