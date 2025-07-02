#!/usr/bin/env python3
# coding=utf-8

"""
Tests for base interface logic.
"""

import pytest
import logging

from logician import DirectStdAllLevelLogger
from logician.configurators.vq.base import SimpleWarningVQLevelOrDefault
from logician.std_log.utils import level_name_mapping


def test_registers_supplied_unknown_levels():
    """
    Registers levels which were previously unknown to the logger.
    """
    levels = {
        7: 'SEVEN-LVL',
        25: 'TWENTY-FIVE-LVL'
    }
    DirectStdAllLevelLogger.register_levels(levels)
    registered_int_levels = logging.getLevelNamesMapping().values()
    assert all(level in registered_int_levels for level in levels)


def test_overrides_supplied_known_levels():
    """
    Overrides levels which were previously known to the logger.
    """
    levels = {
        10: 'DEBUG-LVL',
        20: 'INFO-LVL'
    }
    # assert that previous registered level names are not the same as the newly defined ones.
    assert all(levels[level] != logging.getLevelName(level) for level in levels)
    DirectStdAllLevelLogger.register_levels(levels)
    registered_int_levels = level_name_mapping()
    assert all(level in registered_int_levels for level in levels)
    # assert that newly registered level names are the same as the newly defined ones.
    assert all(levels[level] == logging.getLevelName(level) for level in levels)


def test_supplied_levels_are_not_altered():
    levels = {
        5: 'TRACE-LVL',
        10: 'DEBUG-LVL',
        20: 'INFO-LVL'
    }
    levels_copy = levels.copy()
    DirectStdAllLevelLogger.register_levels(levels)
    assert levels == levels_copy


def test_overrides_supplied_created_levels():
    """
    Overrides levels which were created in this lib and is known to the logger, e.g. TRACE.
    """
    levels = {
        5: 'TRACE-LVL',
        10: 'DEBUG-LVL',
        20: 'INFO-LVL'
    }
    # assert that previous registered level names are not the same as the newly defined ones.
    assert all(levels[level] != logging.getLevelName(level) for level in levels)
    DirectStdAllLevelLogger.register_levels(levels)
    registered_int_levels = level_name_mapping()
    assert all(level in registered_int_levels for level in levels)
    # assert that newly registered level names are the same as the newly defined ones.
    assert all(levels[level] == logging.getLevelName(level) for level in levels)


@pytest.mark.parametrize("level_name_map", [None, {}])
def test_registers_default_if_not_provided(level_name_map):
    DirectStdAllLevelLogger.register_levels(level_name_map)
    registered_levels = level_name_mapping()
    for level in DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP:
        assert level in registered_levels
        assert DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP[level] == registered_levels[level]


class TestSimpleWarningVQLevelOrDefault:
    def test_warns_user_by_default(self):
        s = SimpleWarningVQLevelOrDefault[int]({'v': 10, 'vv': 20})
        with pytest.warns(UserWarning, match="'vvv': Unexpected verbosity value. Choose from 'v' and 'vv'."):
            s.level_or_default('vvv', 'verbosity', 1, ['v', 'vv'])

    def test_can_raise_error_if_directed(self):
        s = SimpleWarningVQLevelOrDefault[int]({'v': 10, 'vv': 20}, warn_only=False)
        with pytest.raises(KeyError, match="'vvv': Unexpected verbosity value. Choose from 'v' and 'vv'."):
            s.level_or_default('vvv', 'verbosity', 1, ['v', 'vv'])

    def test_can_have_a_custom_key_error_handler(self):
        from vt.utils.errors.error_specs.base import WarningWithDefault
        class _ErrOnly[T](WarningWithDefault[T]):
            @property
            def raise_error(self) -> bool:
                return True

            @property
            def warn_only(self) -> bool:
                return not self.raise_error

        s = SimpleWarningVQLevelOrDefault[int]({'v': 10, 'vv': 20}, key_error_handler=_ErrOnly())
        with pytest.raises(KeyError, match="'vvv': Unexpected verbosity value. Choose from 'v' and 'vv'."):
            s.level_or_default('vvv', 'verbosity', 1, ['v', 'vv'])
