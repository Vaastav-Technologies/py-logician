#!/usr/bin/env python3
# coding=utf-8


"""
Constants for verbosity (V) and quietness (Q) configurators.
"""
from typing import Literal

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
Literal denoting how should a {``verbosity-quietness -> logging-level``} dict be structured.

:param T: type of the logger level, for e.g. logger level type is [int | str] for python std logging lib.
"""
