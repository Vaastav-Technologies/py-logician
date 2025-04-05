#!/usr/bin/env python3
# coding=utf-8

"""
Important utilities for std python logging library.
"""
import logging


def level_name_mapping() -> dict[int, str]:
    """
    :return: level -> name mapping from std lib.
    """
    return {level: logging.getLevelName(level) for level in
            sorted(logging.getLevelNamesMapping().values())}


