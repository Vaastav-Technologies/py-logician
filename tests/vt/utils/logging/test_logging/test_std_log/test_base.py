#!/usr/bin/env python3
# coding=utf-8

"""
Tests for base interface logic.
"""
import logging

import pytest

from vt.utils.logging.logging import DirectStdAllLevelLogger


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
    registered_int_levels = logging.getLevelNamesMapping().values()
    assert all(level in registered_int_levels for level in levels)
    # assert that newly registered level names are the same as the newly defined ones.
    assert all(levels[level] == logging.getLevelName(level) for level in levels)


@pytest.mark.parametrize("level_name_map", [None, {}])
def test_registers_default_if_not_provided(level_name_map):
    DirectStdAllLevelLogger.register_levels(level_name_map)
    registered_levels = {l: n for n, l in logging.getLevelNamesMapping().items()}
    for level in DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP:
        assert level in registered_levels
        assert DirectStdAllLevelLogger.DEFAULT_LEVEL_MAP[level] == registered_levels[level]
