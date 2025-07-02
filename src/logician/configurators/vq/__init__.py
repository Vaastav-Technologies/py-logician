#!/usr/bin/env python3
# coding=utf-8


"""
Configurators for verbosity (V) and quietness (Q).
"""

# region configurators.vq.constants re-exports
from logician.configurators.vq.constants import Q_LITERAL as Q_LITERAL
from logician.configurators.vq.constants import V_LITERAL as V_LITERAL
from logician.configurators.vq.constants import VQ_DICT_LITERAL as VQ_DICT_LITERAL
# endregion

# region configurators.vq.base re-exports
from logician.configurators.vq.base import VQConfigurator as VQConfigurator
from logician.configurators.vq.base import VQLevelOrDefault as VQLevelOrDefault
# endregion

from logician.configurators.vq.sep import VQSepConfigurator as VQSepConfigurator

from logician.configurators.vq.comm import VQCommConfigurator as VQCommConfigurator

