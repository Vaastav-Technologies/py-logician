#!/usr/bin/env python3
# coding=utf-8


"""
Logger interfaces for Logger configurators.
"""
import logging
from abc import abstractmethod
from typing import Protocol, Literal, override, get_args, Any

from vt.utils.logging.logging.std_log.base import DirectStdAllLevelLogger
from vt.utils.logging.warnings import vt_warn, Warner


class LoggerConfigurator(Protocol):
    """
    Stores configuration information to configure the std python logger.
    """

    @abstractmethod
    def configure(self, logger: logging.Logger) -> DirectStdAllLevelLogger:
        """
        Configure the std python logger for various formatting quick-hands.

        :param logger: std python logger
        :return: A configured All level logging std python logger.
        """
        pass


V_LITERAL = Literal['v', 'vv', 'vvv']
"""
Verbosity literal. Progressively denotes more and more verbosity.
"""
Q_LITERAL = Literal['q', 'qq', 'qqq']
"""
Quietness literal. Progressively denotes more and more quietness.
"""
type VQ_DICT_LITERAL[T] = dict[V_LITERAL | Q_LITERAL, T]
"""
Literal denoting how should a {``verbosity-quietness -> logging-level``} dict should be structured.

:param T: type of the logger level, for e.g. logger level type is [int | str] for python std logging lib.
"""


class VQConfigurator[T](Protocol):
    """
    Configurator for verbosity and quietness configurations.
    """

    @property
    @abstractmethod
    def vq_level_map(self) -> VQ_DICT_LITERAL[T]:
        """
        :return: A dictionary containing verbosity|quietness -> logging.level mapping.
        """
        ...


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


class DefaultOrError[T](Protocol):

    def handle_key_error(self, key_error: KeyError, emphasis: str, default_level: T,
                         choices: list[Any]) -> T:
        """
        Subclasses will decide how to treat the ``KeyError`` from ``level_or_default()``.

        :param key_error: The ``KeyError`` raised from ``level_or_default()``.
        :param emphasis: strings '`verbosity`' or '`quietness`'.
        :param default_level: logging level to be returned if ``ver_qui`` is ``None``.
        :param choices: What are the choices for `verbosity` or `quietness`.
        :return: ``default_level``.
        :raise KeyError: if verbosity and quietness are absent in ``vq_level_map`` and ``self.handle_key_error()``
            decides to re raise the error.
        """
        errmsg = f"Unexpected {emphasis} value. Choose from {choices}."
        if self.raise_error:
            raise KeyError(f"{key_error}: {errmsg}")
        return default_level

    @property
    @abstractmethod
    def raise_error(self) -> bool:
        ...


class RaiseError[T](DefaultOrError[T]):

    def __init__(self, raise_error: bool = True):
        self._raise_error = raise_error

    @property
    @abstractmethod
    def raise_error(self) -> bool:
        return self._raise_error


class WarningWithDefault[T](DefaultOrError[T], Warner, Protocol):

    @override
    def handle_key_error(self, key_error: KeyError, emphasis: str, default_level: T,
                         choices: list[Any]) -> T:
        """
        Subclasses will decide how to treat the ``KeyError`` from ``level_or_default()``.

        :param key_error: The ``KeyError`` raised from ``level_or_default()``.
        :param emphasis: strings '`verbosity`' or '`quietness`'.
        :param default_level: logging level to be returned if ``ver_qui`` is ``None``.
        :param choices: What are the choices for `verbosity` or `quietness`.
        :return: ``default_level``.
        :raise KeyError: if verbosity and quietness are absent in ``vq_level_map`` and ``self.handle_key_error()``
            decides to re raise the error.
        """
        errmsg = f"Unexpected {emphasis} value. Choose from {choices}."
        if self.warn_only:
            vt_warn(f"{key_error}: {errmsg}")
        else:
            raise KeyError(f"{key_error}: {errmsg}")
        return default_level


class SimpleWarningWithDefault[T](WarningWithDefault[T]):

    def __init__(self, warn_only: bool = True):
        self._warn_only = warn_only

    @override
    @property
    def warn_only(self) -> bool:
        return self._warn_only

    @override
    @property
    def raise_error(self) -> bool:
        return not self.warn_only


class VQLevelOrDefault[T](VQConfigurator[T], Protocol):
    """
    Implementation interface to facilitate getting a logging level from VQConfigurator.
    """

    def level_or_default(self, ver_qui: V_LITERAL | Q_LITERAL | None,
                         emphasis: Literal['verbosity', 'quietness', 'verbosity or quietness'],
                         default_level: T, choices: list[Any]) -> T:
        """
        :param ver_qui: verbosity or quietness.
        :param emphasis: strings '`verbosity`' or '`quietness`'.
        :param default_level: logging level to be returned if ``ver_qui`` is ``None``.
        :param choices: What are the choices for `verbosity` or `quietness`.
        :return: calculated logging level from ``ver_qui`` or ``default_level`` if ``ver_qui`` is ``None``.
        :raise KeyError: if verbosity and quietness are absent in ``vq_level_map`` and ``self.handle_key_error()``
            decides to re raise the error.
        """
        if ver_qui:
            try:
                return self.vq_level_map[ver_qui]
            except KeyError as e:
                return self.key_error_handler.handle_key_error(e, emphasis, default_level, choices)
        else:
            return default_level

    @property
    @abstractmethod
    def key_error_handler(self) -> DefaultOrError[T]:
        ...


class SimpleWarningVQLevelOrDefault[T](VQLevelOrDefault[T], Warner):

    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T], warn_only: bool,
                 key_error_handler: WarningWithDefault[T] | None = None):
        self._vq_level_map = vq_level_map
        self._warn_only = warn_only
        if key_error_handler:
            self._key_error_handler = key_error_handler
        else:
            self._key_error_handler = SimpleWarningWithDefault[T](warn_only=warn_only)

    @override
    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[T]:
        return self._vq_level_map

    @override
    @property
    def warn_only(self) -> bool:
        return self._warn_only

    @property
    def key_error_handler(self) -> WarningWithDefault[T]:
        return self._key_error_handler


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
            self.level_or_default_handler = SimpleWarningVQLevelOrDefault(vq_level_map, warn_only)

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
        ValueError: 'verbosity' and 'quietness' cannot be given together.

        Only warn if ``warn_only`` is provided ``True``::

        >>> with warnings.catch_warnings():
        ...     with contextlib.redirect_stderr(sys.stdout):
        ...         VQSepExclusive({}, True).validate('v', 'q')
        UserWarning: 'verbosity' and 'quietness' cannot be given together.
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
            warn_str = "'verbosity' and 'quietness' cannot be given together."
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
            ValueError: 'verbosity' and 'quietness' cannot be given together.

            Only warn if warn_only is provided True and return the default_value:

            >>> with warnings.catch_warnings():
            ...     with contextlib.redirect_stderr(sys.stdout):
            ...         VQSepExclusive[int]({'v': 20}, True).get_effective_level('v', 'q', 10)
            UserWarning: 'verbosity' and 'quietness' cannot be given together.
            10

        Level inquiry::

            Get queried verbosity:

            >>> VQSepExclusive[int]({'v': 20}).get_effective_level('v', None, 10)
            20

            Return default_level if queried verbosity is not registered and warn_only is True:

            >>> with warnings.catch_warnings():
            ...     with contextlib.redirect_stderr(sys.stdout):
            ...         VQSepExclusive[int]({'v': 20}, True).get_effective_level('vv', None, 10)
            UserWarning: 'vv': Unexpected verbosity value. Choose from ('v', 'vv', 'vvv').
            10

            Raise KeyError if queried verbosity is not registered and warn_only is False or not provided:

            >>> VQSepExclusive[int]({'v': 20}).get_effective_level('vv', None, 10)
            Traceback (most recent call last):
            ...
            KeyError: "'vv': Unexpected verbosity value. Choose from ('v', 'vv', 'vvv')."

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
