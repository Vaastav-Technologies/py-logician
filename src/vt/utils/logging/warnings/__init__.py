#!/usr/bin/env python3
# coding=utf-8


"""
Python warnings related helpers.
"""


import warnings
from contextlib import contextmanager
from typing import Type


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
