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
    pass
