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
    @abstractmethod
    def configure(self, logger: logging.Logger, level: int | str = logging.WARNING) -> DirectStdAllLevelLogger:
        pass
