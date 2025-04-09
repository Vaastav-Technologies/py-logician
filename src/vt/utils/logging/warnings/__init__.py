#!/usr/bin/env python3
# coding=utf-8


"""
Python warnings related helpers.
"""


import warnings
from abc import abstractmethod
from contextlib import contextmanager
from typing import Type, Protocol


@contextmanager
def suppress_warning_stacktrace(fmt: str = "{category}: {message}\n"):
    """
    Context manager to suppress the stack trace for warnings,
    showing only the message with the warning label.

    This context manager allows to alter the warning print format by the caller, following are supported::

        - category - The warning category, e.g. UserWarning.
        - message - The warning message
        - filename - The name of the file to be printed with the warning.
        - lineno - lineno of the warning generator file to be printed with the warning.
        - line - The warning line.

    :param fmt: Warning print format can be altered by the client code.
    """
    original_format = warnings.formatwarning
    def no_stack_trace(message: Warning | str,
                  category: Type[Warning],
                  filename: str,
                  lineno: int,
                  line: str | None = None) -> str:
        return fmt.format(message=message, category=category.__name__, filename=filename, lineno=lineno, line=line)
    warnings.formatwarning = no_stack_trace
    try:
        yield fmt
    finally:
        warnings.formatwarning = original_format


def vt_warn(*args, fmt = "{category}: {message}\n", suppress_stacktrace = True, stack_level = 2, **kwargs):
    """
    Warning function to warn without showcasing warning stack-trace. Uses ``suppress_warning_stacktrace`` internally.

    Required warning message print format can be supplied in the ``fmt`` param,  following are supported::

        - category - The warning category, e.g. UserWarning.
        - message - The warning message
        - filename - The name of the file to be printed with the warning.
        - lineno - lineno of the warning generator file to be printed with the warning.
        - line - The warning line.

    :param args: arguments to the ``warnings.warn()`` function.
    :param fmt: Warning print format can be altered by the client code.
    :param suppress_stacktrace: Whether to suppress the stack trace of warnings.
    :param stack_level: The ``stacklevel`` argument to be passed to ``warnings.warn()``.
    :param kwargs: keyword-args to be passed to ``warnings.warn()``.
    """
    if suppress_stacktrace:
        with suppress_warning_stacktrace(fmt):
            warnings.warn(*args, stacklevel=stack_level, **kwargs)
    else:
        warnings.warn(*args, stacklevel=stack_level, **kwargs)


class Warner(Protocol):
    """
    Interface denoting that a class method can potentially warn instead of directly raising an Error.
    """

    @property
    @abstractmethod
    def warn_only(self) -> bool:
        """
        :return: ``True`` if a warning is to be issued instead of raising an error on an exceptional/erroneous
            circumstance. ``False`` otherwise.
        """
        ...
