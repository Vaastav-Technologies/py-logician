#!/usr/bin/env python3
# coding=utf-8

"""
Classes w.r.t implementation inheritance for base logger are defined here.
"""

from abc import ABC

from vt.utils.logging.logging import MinLevelLogger, AllLevelLogger
from vt.utils.logging.logging.base import _MinLevelLogger


class _ProtocolMinLevelLoggerImplBase(_MinLevelLogger, ABC):
    pass


class ProtocolMinLevelLoggerImplABC(_ProtocolMinLevelLoggerImplBase, MinLevelLogger, ABC):
    pass


class AllLevelLoggerImplABC(_ProtocolMinLevelLoggerImplBase, AllLevelLogger, ABC):
    pass
