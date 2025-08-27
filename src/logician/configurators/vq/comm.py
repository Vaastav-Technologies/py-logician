#!/usr/bin/env python3
# coding=utf-8


"""
Configurators for verbosity (V) and quietness (Q) that accept verbosity and quietness as one inclusive argument.

Useful when users know that verbosity and quietness will arrive in one parameter, for e.g. a CLI which accepts
environment variables as such:

- LGCN_ALL_LOG=vv
- CCC_LIB_LOG = qq

Here the value for a simple environment variable maybe vv or qq and hence can arrive in a single parameter.
"""

from abc import abstractmethod
from typing import Protocol, override

from logician.configurators.vq import VQConfigurator, V_LITERAL, Q_LITERAL, VQ_DICT_LITERAL, \
    VQLevelOrDefault
from logician.configurators.vq.base import SimpleWarningVQLevelOrDefault


class VQCommConfigurator[T](VQConfigurator[T], Protocol):
    """
    Configurator which takes verbosity and quietness commonly (in a single argument) for configuration.
    """

    @abstractmethod
    def validate(self, ver_qui: V_LITERAL | Q_LITERAL | None) -> bool:
        """
        Validate whether the supplied verbosity or quietness are valid.

        :param ver_qui: verbosity or quietness.
        :return: ``True`` if inputs are valid, ``False`` otherwise.
        :raise ValueError: if values for ``ver_qui`` are invalid and subclass decides to raise the error.
        """
        ...

    @abstractmethod
    def get_effective_level(self, ver_qui: V_LITERAL | Q_LITERAL | None, default_level: T) -> T:
        """
        Get the effective level for supplied verbosity or quietness.

        :param ver_qui: verbosity or quietness.
        :param default_level: returned if both verbosity or quietness are ``None`` or not supplied.
        :return: computed level for verbosity and quietness or ``default_level`` if verbosity or quietness
            are ``None``.
        :raise KeyError: if the verbosity or quietness is not found in the ``vq_level_map`` and the subclass decides
            to raise error for this.
        """
        ...


class VQCommon[T](VQCommConfigurator[T]):
    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T], warn_only: bool = False,
                 level_or_default_handler: VQLevelOrDefault[T] | None = None):
        """
        Treats verbosity and quietness as one inclusive argument.

        Treats such conditions as an error::

            - supplied verbosity or quietness is not within the ``vq_level_map``.

        :param vq_level_map: A dictionary containing verbosity|quietness -> logging.level mapping.
        :param warn_only: Only warn on potential errors instead of raising an Error.
        :param level_or_default_handler: Level computer. Defaults to ``SimpleWarningVQLevelOrDefault`` if ``None`` or
            not supplied.
        """
        self._vq_level_map = vq_level_map
        if level_or_default_handler:
            self.level_or_default_handler = level_or_default_handler
        else:
            self.level_or_default_handler = SimpleWarningVQLevelOrDefault(vq_level_map, warn_only=warn_only)

    @override
    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[T]:
        return self._vq_level_map

    @override
    def validate(self, ver_qui: V_LITERAL | Q_LITERAL | None) -> bool:
        """
        Examples::

        >>> VQCommon({}).validate('v')
        False


        >>> VQCommon({}).validate('q')
        False

        >>> VQCommon({}).validate('vqn') # noqa
        False

        >>> VQCommon[int]({'v': 20}).validate('v')
        True


        >>> VQCommon({'v': 20, 'q': 1}).validate('q')
        True

        :return: ``True`` if ``ver_qui`` is in the assigned level map, else ``False``.
        """
        if ver_qui in self.vq_level_map:
            return True
        return False

    @override
    def get_effective_level(self, ver_qui: V_LITERAL | Q_LITERAL | None, default_level: T) -> T:
        """
        Get effective level by treating verbosity and quietness as single argument.

        Examples::

        >>> import sys
        >>> import contextlib
        >>> import warnings

        Level inquiry::

            Get queried verbosity:

            >>> VQCommon[int]({'v': 20}).get_effective_level('v', 10)
            20

            Return default_level if queried verbosity is not registered and warn_only is True:

            >>> with warnings.catch_warnings(record=True) as w:
            ...     VQCommon[int]({'v': 20, 'q': 1}, True).get_effective_level('vv', 10)
            ...     assert "'vv': Unexpected verbosity or quietness value. Choose from 'v' and 'q'." in str(w.pop().message)
            10

            Raise KeyError if queried verbosity or quietness is not registered and warn_only is False or not provided:

            >>> VQCommon[int]({'v': 20, 'qqq': 70}).get_effective_level('qq', 10)
            Traceback (most recent call last):
            ...
            KeyError: "'qq': Unexpected verbosity or quietness value. Choose from 'v' and 'qqq'."

        :param ver_qui: `verbosity` or `quietness`.
        :param default_level: level to return when verbosity and quietness are not in the ``vq_level_map``.
        :returns: corresponding logging level according to verbosity and quietness calculations.
            ``default_level`` if both verbosity and quietness are ``None`` or not supplied.
            ``default_level`` if both are not supplied and ``warn_only`` is ``True``.
        :rtype T: a type
        :raise KeyError: if verbosity and quietness are absent in ``vq_level_map`` and ``warn_only`` is ``False``.
        """
        if ver_qui:
            level = self.level_or_default_handler.level_or_default(ver_qui,
                                                                   'verbosity or quietness', default_level,
                                                                   list(self.vq_level_map.keys()))
        else:
            level = default_level
        return level
