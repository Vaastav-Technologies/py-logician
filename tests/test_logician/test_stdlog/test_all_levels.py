#!/usr/bin/env python3
# coding=utf-8

"""
Tests for implementation of logger impl.
"""
import logging
from unittest.mock import patch

import pytest

from logician.stdlog import TRACE_LOG_LEVEL, TIMED_DETAIL_LOG_FMT, DEFAULT_STACK_LEVEL
from logician.stdlog.all_levels_impl import DirectAllLevelLoggerImpl, TempSetCmdLvlName


def test_ensure_correct_logging_lines():
    # logging.basicConfig(level=TRACE_LOG_LEVEL)
    # logging.basicConfig(level=TRACE_LOG_LEVEL, format=TIMED_DETAIL_LOG_FMT)
    log = logging.getLogger('correct-logging-lines')
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log.addHandler(sh)
    log.setLevel(TRACE_LOG_LEVEL)
    # logging.basicConfig(level=TRACE_LOG_LEVEL)
    log.info('an info')
    log.error('an error')
    logger = DirectAllLevelLoggerImpl(log, DEFAULT_STACK_LEVEL)
    logger.info('initialised info')
    logger.fatal('initialised fatal')


class TestSuppliedCmdName:
    def test_cmd_name_set_when_cmd_is_passed(self):
        """
        log.cmd() sets the cmd_lvl_name to the passed level when cmd name is passed.
        """
        log = logging.getLogger('cmd-name-set')
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
        log.addHandler(sh)
        log.setLevel(TRACE_LOG_LEVEL)
        log.info('an info')
        logger = DirectAllLevelLoggerImpl(log, DEFAULT_STACK_LEVEL)
        logger.info('initialised info')
        logger.cmd('initialised cmd', 'A command')

    @pytest.mark.parametrize('cmd_name', ['', ' ', '\n', """   """])
    def test_warns_when_empty_cmd_name_passed(self, cmd_name):
        log = logging.getLogger(f'cmd-name-set-{cmd_name}')
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
        log.addHandler(sh)
        log.setLevel(TRACE_LOG_LEVEL)
        log.info('an info')
        logger = DirectAllLevelLoggerImpl(log, DEFAULT_STACK_LEVEL)
        logger.info('initialised info')
        with pytest.warns(match=r"Supplied log level name for command log level [\d]+ is empty."):
            logger.cmd('initialised cmd', cmd_name)

    def test_warns_when_no_cmd_name_passed(self):
        log = logging.getLogger('cmd-name-set-None')
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
        log.addHandler(sh)
        log.setLevel(TRACE_LOG_LEVEL)
        log.info('an info')
        logger = DirectAllLevelLoggerImpl(log, DEFAULT_STACK_LEVEL)
        logger.info('initialised info')
        logger.cmd('initialised cmd', None)

@pytest.mark.parametrize('cmd_lvl_name', ["CMD", None])
def test_ctx_mgr_called_when_cmd_lvl_enabled(cmd_lvl_name):
    log = logging.getLogger(f'cmd-lvl_enabled-{cmd_lvl_name}')
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log.addHandler(sh)
    log.setLevel(TRACE_LOG_LEVEL)
    log.info('an info')
    logger = DirectAllLevelLoggerImpl(log, DEFAULT_STACK_LEVEL)
    logger.info('initialised info')
    method = TempSetCmdLvlName
    with patch(f"{method.__module__}.{method.__qualname__}") as mocked_fn:
        logger.cmd("Command logged", cmd_lvl_name)
        mocked_fn.assert_called_once_with(cmd_lvl_name)


@pytest.mark.parametrize('cmd_lvl_name', ["CMD", None])
def test_ctx_mgr_not_called_when_cmd_lvl_disabled(cmd_lvl_name):
    log = logging.getLogger(f'cmd-lvl_disabled-{cmd_lvl_name}')
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log.addHandler(sh)
    log.info('an info')
    logger = DirectAllLevelLoggerImpl(log, DEFAULT_STACK_LEVEL)
    logger.info('initialised info')
    method = TempSetCmdLvlName
    with patch(f"{method.__module__}.{method.__qualname__}") as mocked_fn:
        cmd_lvl_name = "CMD"
        logger.cmd("Command logged", cmd_lvl_name)
        mocked_fn.assert_not_called()
