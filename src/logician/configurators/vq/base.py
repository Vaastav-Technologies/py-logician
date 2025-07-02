#!/usr/bin/env python3
# coding=utf-8


"""
Base interfaces for verbosity (V) and quietness (Q) configurators.
"""
from abc import abstractmethod
from typing import Protocol, Literal, Any, override, overload

from vt.utils.errors.error_specs import DefaultOrError, WarningWithDefault
from vt.utils.errors.error_specs.base import SimpleWarningWithDefault
from vt.utils.errors.warnings import Warner

from logician.configurators.vq import VQ_DICT_LITERAL, V_LITERAL, Q_LITERAL

from logician import errmsg_creator


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


class VQLevelOrDefault[T](VQConfigurator[T], Protocol):
    """
    Interface to facilitate getting a logging level from VQConfigurator.
    """

    def level_or_default(self, ver_qui: V_LITERAL | Q_LITERAL | None,
                         emphasis: Literal['verbosity', 'quietness', 'verbosity or quietness'],
                         default_level: T, choices: list[Any]) -> T:
        """
        :param ver_qui: verbosity or quietness.
        :param emphasis: strings '`verbosity`' or '`quietness`'.
        :param default_level: logging level to be returned if ``ver_qui`` is ``None``.
        :param choices: What are the choices for `verbosity` or `quietness` or 'verbosity or quietness'.
        :return: calculated logging level from ``ver_qui`` or ``default_level`` if ``ver_qui`` is ``None``.
        :raise KeyError: if verbosity and quietness are absent in ``vq_level_map`` and ``self.key_error_handler``
            decides to re raise the error.
        """
        if ver_qui:
            try:
                return self.vq_level_map[ver_qui]
            except KeyError as e:
                return self.key_error_handler.handle_key_error(e, default_level, emphasis, choices)
        else:
            return default_level

    @property
    @abstractmethod
    def key_error_handler(self) -> DefaultOrError[T]:
        ...


class SimpleWarningVQLevelOrDefault[T](VQLevelOrDefault[T], Warner):
    @overload
    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T]):
        ...

    @overload
    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T], *, warn_only: bool):
        ...

    @overload
    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T], *, key_error_handler: WarningWithDefault[T]):
        ...

    def __init__(self, vq_level_map: VQ_DICT_LITERAL[T], *, warn_only: bool | None = None,
                 key_error_handler: WarningWithDefault[T] | None = None):
        """
        Simple implementation for ``VQLevelOrDefault``. It can decided by the ``key_error_handler`` on how to handle
        ``KeyError``.

        Default behavior is to simply warn the user on occurrence of a ``KeyError``.

        Fail-fast error examples::

        >>> from vt.utils.errors.error_specs.base import NoErrWarningWithDefault
        >>> vq_levels: VQ_DICT_LITERAL[int] = {'v': 10, 'vv': 5, 'q': 30}

        >>> SimpleWarningVQLevelOrDefault[int](vq_levels, warn_only=False, key_error_handler=NoErrWarningWithDefault())
        Traceback (most recent call last):
        ...
        ValueError: warn_only and key_error_handler are not allowed together


        Correct no error examples::

        >>> _ = SimpleWarningVQLevelOrDefault[int](vq_levels)

        >>> _ = SimpleWarningVQLevelOrDefault[int](vq_levels, warn_only=False)

        >>> _ = SimpleWarningVQLevelOrDefault[int](vq_levels, key_error_handler=NoErrWarningWithDefault())

        :param vq_level_map: verbosity-quietness level map.
        :param warn_only: warn the user of an error? Cannot be provided with ``key_error_handler``.
        :param key_error_handler: A custom ``KeyError`` to handle key errors.
        """
        if warn_only is not None and key_error_handler is not None:
            raise ValueError(errmsg_creator.not_allowed_together('warn_only', 'key_error_handler'))
        self._vq_level_map = vq_level_map
        if key_error_handler:
            self._key_error_handler = key_error_handler
        elif warn_only is not None:
            self._key_error_handler = SimpleWarningWithDefault[T](warn_only=warn_only)
        else:
            # default behavior to just warn user on KeyError.
            self._key_error_handler = SimpleWarningWithDefault[T](warn_only=True)
        self._warn_only = self.key_error_handler.warn_only

    @override
    @property
    def vq_level_map(self) -> VQ_DICT_LITERAL[T]:
        return self._vq_level_map

    @override
    @property
    def warn_only(self) -> bool:
        return self._warn_only

    @override
    @property
    def key_error_handler(self) -> WarningWithDefault[T]:
        return self._key_error_handler
