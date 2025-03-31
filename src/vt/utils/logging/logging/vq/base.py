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
    def log_fmt(self, temp_verbosity: int | None, temp_quietness: int | None) -> str:
        """
        Computes the log format required when verbosity or quietness levels are given. Different log formats can be
        returned for different combinations of the supplied verbosity and quietness levels.

        Note::

            This method must not set/modify the ``verbosity`` and ``quietness`` state variables of the class as this
            is just a query method which eventually gets used by ``set_log_level_vq()`` to either set the log format
            for a logger or can be used by a caller for diagnostic purposes.

        :param temp_verbosity: verbosity level to determine a certain log format.
        :param temp_quietness: quietness level to determine a certain log format.
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
