#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger configurators.
"""


import logging
from abc import abstractmethod
from typing import Protocol

from vt.utils.logging.logging.std_log.base import DirectStdAllLevelLogger


class LoggerConfigurator(Protocol):
    """
    Stores configuration information to configure the std python logger.
    """

    @abstractmethod
    def configure(self, logger: logging.Logger, level: int | str = logging.WARNING,
                  cmd_name: str | None = None) -> DirectStdAllLevelLogger:
        """
        Configure the std python logger for various formatting quick-hands.

        :param logger: std python logger
        :param level: logging level.
        :param cmd_name: The command name to register the command logging level to. If `None`` then the default
            ``COMMAND`` is picked-up and that will be shown on the ``log.cmd()`` call.
        :return: A configured All level logging std python logger.
        """
        pass
