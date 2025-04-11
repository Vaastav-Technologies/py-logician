#!/usr/bin/env python3
# coding=utf-8


"""
Python warning-contexts related helpers tests.
"""


import warnings

import pytest

from vt.utils.errors.warnings import suppress_warning_stacktrace


def use_ctx():
    prev_fmt = warnings.formatwarning
    with pytest.warns(expected_warning=UserWarning, match='with tb'):
        with suppress_warning_stacktrace():
            warnings.warn('a warning with tb')
            assert warnings.formatwarning != prev_fmt
    return prev_fmt


def test_changes_warning_format():
    use_ctx()


def test_restores_warning_format():
    prev_fmt = use_ctx()
    assert warnings.formatwarning == prev_fmt
