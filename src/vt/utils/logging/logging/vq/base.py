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
    def verbosity(self) -> int:
        """
        :return: logger verbosity in int.
        """
        pass


class QuietLogger(ABC):
    """
    Interface declaring that a logger supports quietness settings.

    Quietness is mainly measured in int.
    """
    @property
    @abstractmethod
    def quietness(self) -> int:
        """
        :return: logger quietness in int.
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
    def set_log_level_vq(self, verbosity: int, quietness: int) -> None:
        """
        Set the log level according to the verbosity and quietness supplied.

        :param verbosity: verbosity level of the logger.
        :param quietness: quietness level of the logger.
        """
        pass
