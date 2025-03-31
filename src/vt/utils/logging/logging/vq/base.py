#!/usr/bin/env python3
# coding=utf-8


"""
Interfaces for loggers that respect verbose and quiet configurations.
"""


from abc import ABC, abstractmethod


class VerboseLogger(ABC):
    """
    Interface declaring that a logger supports verbosity settings.

    Verbosity is mainly measured in int.
    """
    @property
    @abstractmethod
    def verbosity(self) -> int | None:
        """
        :return: logger verbosity in int. ``None`` if verbosity remains unset.
        """
        pass


class QuietLogger(ABC):
    """
    Interface declaring that a logger supports quietness settings.

    Quietness is mainly measured in int.
    """
    @property
    @abstractmethod
    def quietness(self) -> int | None:
        """
        :return: logger quietness in int. ``None`` if quietness remains unset.
        """
        pass


class VerboseQuietLogger(VerboseLogger, QuietLogger, ABC):
    """
    Interface declaring that a logger supports verbosity and quietness settings.

    Verbosity and Quietness is mainly measured in int.
    """
    @abstractmethod
    def log_fmt(self) -> str:
        """
        :return: desired log format for the supplied verbosity or quietness level.
        """
        pass

    @abstractmethod
    def set_log_level_vq(self, verbosity: int | None, quietness: int | None) -> None:
        """
        Set the log level according to the verbosity and quietness supplied.

        :param verbosity: verbosity level of the logger.
        :param quietness: quietness level of the logger.
        """
        pass
