#!/usr/bin/env python3
# coding=utf-8

"""
Logging interfaces for the standard logging library of python.
"""
from abc import ABC
from typing import Protocol, Any, Mapping

from vt.utils.logging.logging import MinLogProtocol
from vt.utils.logging.logging.base import _MinLevelLogger, FatalLevelLogger, ExceptionLevelLogger


class StdLogProtocol(MinLogProtocol, Protocol):
    """
    Logger protocol that is followed (for methods) by the python std logging.

    Two additional methods are added on top of the MinLogProtocol::

        - fatal
        - exception

    along with properties that python std logger provides::

        - name
        - level
        - disabled
    """
    name: str
    level: int
    disabled: bool

    def fatal(self, msg: str, *args, **kwargs) -> None:
        ...

    # noinspection SpellCheckingInspection
    # required for the param stack-level because this method signature from the protocol needs to correctly match that
    # of the std logging method signature.
    def exception(self, msg: object, *args: object, exc_info: Any = ..., stack_info: bool = ...,
                  stacklevel: int = ..., extra: Mapping[str, object] | None = ...) -> None:
        ...


class StdLevelLogger(_MinLevelLogger, FatalLevelLogger, ExceptionLevelLogger, ABC):
    """
    Logger that implements python standard logging methods::

        - debug
        - info
        - warning
        - error
        - critical
        - fatal
        - exception
    """
    pass
