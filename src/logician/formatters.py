#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger formatters.
"""

from abc import abstractmethod
from typing import Protocol


class LogLevelFmt[L, F](Protocol):
    """
    Interface to specify how log levels should impact the logging formats.

    For e.g.::

        ERROR: an error occurred.
        logger.name: INFO: some information
        logger.name: DEBUG: [filename.py - func()]: some debug info
        2025-04-03 20:59:39,418: TRACE: [filename.py:218 - func()]: some trace info

    see ``DiffLevelDiffFmt`` for behavior on different log format for different logging levels.

    or the format remains same throughout all logging levels, see ``AllLevelSameFmt``.

    L - type of ``level`` of the logger, e.g. ``int`` for python std log.

    F – type of the returned format, e.g. ``str`` for python std log.
    """

    @abstractmethod
    def fmt(self, level: L) -> F:
        """
        :param level: ``level`` for which the log ``format`` is to be queried.
        :return: format for the queried ``level``.
        """
        pass  # pragma: no cover


class AllLevelSameFmt[L, F](LogLevelFmt[L, F], Protocol):
    """
    Interface to specify how different log levels infer the same logging formats.

    For e.g.::

        - least verbose ERROR level.
        ERROR: an error occurred.

        - less verbose INFO level.
        INFO: some information

        - verbose DEBUG level.
        DEBUG: some debug info

        - most verbose TRACE level.
        TRACE: some trace info
    """

    pass


class DiffLevelDiffFmt[L, F](LogLevelFmt[L, F], Protocol):
    """
    Interface to specify how different log levels should impact the logging formats.

    For e.g.::

        - least verbose ERROR level.
        ERROR: an error occurred.

        - less verbose INFO level.
        logger.name: INFO: some information

        - verbose DEBUG level.
        logger.name: DEBUG: [filename.py - func()]: some debug info

        - most verbose TRACE level.
        2025-04-03 20:59:39,418: TRACE: [filename.py:218 - func()]: some trace info
    """

    @abstractmethod
    def next_approx_level(self, missing_level: L) -> L:
        """
        :param missing_level: A level that was not registered in the logger.
        :return: next approx level if a ``missing_level`` is queried which wasn't already registered in the logger.
        """
        pass  # pragma: no cover
