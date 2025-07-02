#!/usr/bin/env python3
# coding=utf-8


"""
Configurators for verbosity (V) and quietness (Q) that accept verbosity and quietness as exclusive separate arguments.

Useful when users know that verbosity and quietness will arrive in separate parameters, for e.g. a CLI which accepts
-v, -vv ... etc. for verbosity and -qq, -qqq ... etc. for quietness.
"""

from abc import abstractmethod
from typing import Protocol, override

from vt.utils.errors.warnings import vt_warn

from logician import errmsg_creator
from logician.configurators.vq import VQConfigurator, V_LITERAL, Q_LITERAL, VQ_DICT_LITERAL, \
    VQLevelOrDefault
from logician.configurators.vq.base import SimpleWarningVQLevelOrDefault


class VQSepConfigurator[T](VQConfigurator[T], Protocol):
    """
    Configurator which takes verbosity and quietness separately (as separate arguments) for configuration.
    """

    @abstractmethod
    def validate(self, verbosity: V_LITERAL | None, quietness: Q_LITERAL | None) -> bool:
        """
        Validate whether the supplied verbosity and quietness are valid.

        :param verbosity: verbosity.
        :param quietness: quietness.
        :return: ``True`` if inputs are valid, ``False`` otherwise.
        """
        ...

    @abstractmethod
    def get_effective_level(self, verbosity: V_LITERAL | None, quietness: Q_LITERAL | None, default_level: T) -> T:
        """
        Get the effective level for supplied verbosity and quietness.

        :param verbosity: verbosity.
        :param quietness: quietness.
        :param default_level: returned if both verbosity and quietness are ``None`` or not supplied.
        :return: computed level for verbosity and quietness or ``default_level`` if both verbosity and quietness
            are ``None``.
        """
        ...


class VQSepExclusive[T](VQSepConfigurator[T]):
    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T], warn_only: bool = False,
                 level_or_default_handler: VQLevelOrDefault[T] | None = None):
        """
        Treats verbosity and quietness as separate and exclusive, i.e. both cannot be given together.

        Treats such conditions as an error::

            - verbosity and quietness are provided together.
            - supplied verbosity or quietness is not within the ``vq_level_map``.

        :param vq_level_map: A dictionary containing verbosity|quietness -> logging.level mapping.
        :param warn_only: Only warn on potential errors instead of raising an Error.
        """
        self._vq_level_map = vq_level_map
        self.warn_only = warn_only
        if level_or_default_handler:
            self.level_or_default_handler = level_or_default_handler
        else:
            self.level_or_default_handler = SimpleWarningVQLevelOrDefault(vq_level_map, warn_only=warn_only)

    @override
    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[T]:
        return self._vq_level_map

    @override
    def validate(self, verbosity: V_LITERAL | None, quietness: Q_LITERAL | None) -> bool:
        """
        ``verbosity`` and ``quietness`` are not accepted together.

        Examples::

        >>> import sys
        >>> import contextlib
        >>> import warnings

        Raise error if ``warn_only`` is ``False`` or not provided::

        >>> VQSepExclusive({}).validate('v', 'q')
        Traceback (most recent call last):
        ...
        ValueError: verbosity and quietness are not allowed together

        Only warn if ``warn_only`` is provided ``True``::

        >>> with warnings.catch_warnings(record=True) as w:
        ...     VQSepExclusive({}, True).validate('v', 'q')
        ...     assert "verbosity and quietness are not allowed together" in str(w.pop().message)
        False

        Return ``True`` if only one verbosity is supplied::

        >>> VQSepExclusive({}).validate('v', None)
        True

        Return ``True`` if only one quietness is supplied::

        >>> VQSepExclusive({}).validate(None, 'q')
        True

        Return ``True`` if both are ``None``::

        >>> VQSepExclusive({}).validate(None, None)
        True

        :raise ValueError: if both verbosity and quietness are given and If ``self.warn_only`` is ``False``.
        :return: If ``self.warn_only`` is ``True`` - ``True`` if inputs are valid, ``False`` otherwise.
        """
        if verbosity and quietness:
            warn_str = errmsg_creator.not_allowed_together('verbosity', 'quietness')
            if self.warn_only:
                vt_warn(warn_str)
                return False
            else:
                raise ValueError(warn_str)
        else:
            return True

    @override
    def get_effective_level(self, verbosity: V_LITERAL | None, quietness: Q_LITERAL | None, default_level: T) -> T:
        """
        Get effective level by treating verbosity and quietness as separate entities.

        Note::

            verbosity and quietness are not to be provided together.

        Examples::

        >>> import sys
        >>> import contextlib
        >>> import warnings

        Both verbosity and quietness provided together::

            warn_only is not provided or is False:

            >>> VQSepExclusive({}).get_effective_level('v', 'q', 10)
            Traceback (most recent call last):
            ...
            ValueError: verbosity and quietness are not allowed together

            Only warn if warn_only is provided True and return the default_value:

            >>> with warnings.catch_warnings(record=True) as w:
            ...     VQSepExclusive[int]({'v': 20}, True).get_effective_level('v', 'q', 10)
            ...     assert "verbosity and quietness are not allowed together" in str(w.pop().message)
            10

        Level inquiry::

            Get queried verbosity:

            >>> VQSepExclusive[int]({'v': 20}).get_effective_level('v', None, 10)
            20

            Return default_level if queried verbosity is not registered and warn_only is True:

            >>> with warnings.catch_warnings(record=True) as w:
            ...     VQSepExclusive[int]({'v': 20}, True).get_effective_level('vv', None, 10)
            ...     assert "'vv': Unexpected verbosity value. Choose from 'v'." in str(w.pop().message)
            10

            Raise KeyError if queried verbosity is not registered and warn_only is False or not provided:

            >>> VQSepExclusive[int]({'v': 20}).get_effective_level('vv', None, 10)
            Traceback (most recent call last):
            ...
            KeyError: "'vv': Unexpected verbosity value. Choose from 'v'."

        :param verbosity: verbosity.
        :param quietness: quietness.
        :param default_level: level to return when verbosity and quietness are not in the ``vq_level_map``.
        :returns: corresponding logging level according to verbosity and quietness calculations.
            ``default_level`` if both verbosity and quietness are ``None`` or not supplied.
            ``default_level`` if both are not supplied and ``warn_only`` is ``True``.
        :rtype T: a type
        :raise KeyError: if verbosity and quietness are absent in ``vq_level_map`` and ``warn_only`` is ``False``.
        :raise ValueError: If both verbosity and quietness are given and ``self.warn_only`` is ``False``.
        """
        if not self.validate(verbosity, quietness):
            level = default_level
        else:
            if verbosity:
                level = self.level_or_default_handler.level_or_default(verbosity,
                                                                       'verbosity', default_level,
                                                                       list(self.vq_level_map.keys()))
            elif quietness:
                level = self.level_or_default_handler.level_or_default(quietness,
                                                                       'quietness', default_level,
                                                                       list(self.vq_level_map.keys()))
            else:
                level = default_level
        return level
