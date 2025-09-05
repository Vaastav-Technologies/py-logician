#!/usr/bin/env python3
# coding=utf-8

import logging

import pytest


@pytest.fixture(autouse=True)
def reset_logging_levels(monkeypatch):
    orig_level_to_name = logging._levelToName.copy()
    orig_name_to_level = logging._nameToLevel.copy()

    monkeypatch.setattr(logging, "_levelToName", orig_level_to_name.copy())
    monkeypatch.setattr(logging, "_nameToLevel", orig_name_to_level.copy())
