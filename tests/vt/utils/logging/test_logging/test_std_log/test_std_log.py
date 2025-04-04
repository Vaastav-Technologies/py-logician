#!/usr/bin/env python3
# coding=utf-8


import logging

import pytest

from vt.utils.logging.logging.std_log import TRACE_LOG_LEVEL
from vt.utils.logging.logging.std_log.basic_logger import DirectAllLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import DirectAllLevelLoggerImpl

TIMED_DETAIL_LOG_FMT = '%(asctime)s: %(name)s: [%(levelname)s]: [%(filename)s:%(lineno)d - ' \
                       '%(funcName)10s() ]: %(message)s'


@pytest.mark.parametrize("level_logger", [DirectAllLevelLogger])
@pytest.mark.parametrize("logger_impl", [DirectAllLevelLoggerImpl])
def test_initial_logging(level_logger, logger_impl):
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger(f"{level_logger.__qualname__}/{logger_impl.__qualname__}")
    log.addHandler(sh)
    log.setLevel(logging.DEBUG)
    logger = level_logger(logger_impl(log))
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')
    try:
        raise ValueError('A value is wrong.')
    except ValueError:
        logger.exception('an exception')
    logger.fatal('fatal message')


def test_logging_basic_types():
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger(f"all-basic-types-logging")
    logger = DirectAllLevelLogger(DirectAllLevelLoggerImpl(log))
    logger.underlying_logger.addHandler(sh)
    logger.underlying_logger.setLevel(TRACE_LOG_LEVEL)
    d = {1: 2, 2: 3, None: 4}
    logger.trace(d)
    l = [1, 2, 3, 4, None]
    logger.debug(l)
    t = (1, 2, 3, None)
    logger.info(t)
    s = {1, 2, 3, 4, None}
    logger.notice(s)
    logger.success('success {}'.format(d))
    logger.warning('warning %s', l)
    logger.error('error %(t)s', {'t': t})
    try:
        raise ValueError(l)
    except ValueError:
        logger.exception('Exception: ')


def test_all_initial_logging():
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger(f"all-init-logging")
    logger = DirectAllLevelLogger(DirectAllLevelLoggerImpl(log))
    logger.underlying_logger.addHandler(sh)
    logger.underlying_logger.setLevel(TRACE_LOG_LEVEL)
    logger.trace('trace message')
    logger.debug('debug message')
    logger.info('info message')
    logger.success('success message')
    logger.notice('notice message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')
    try:
        raise ValueError('A value is wrong.')
    except ValueError:
        logger.exception('an exception')
    logger.fatal('fatal message')
