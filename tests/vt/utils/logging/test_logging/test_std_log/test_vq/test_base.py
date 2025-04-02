#!/usr/bin/env python3
# coding=utf-8
import logging

import pytest

from vt.utils.logging.logging.std_log import TRACE_LOG_LEVEL
from vt.utils.logging.logging.std_log.basic_logger_impl import DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.vq.base import VQDirectStdLevelLogger, VQDirectAllLevelLogger

TIMED_DETAIL_LOG_FMT = '%(asctime)s: %(name)s: [%(levelname)s]: [%(filename)s:%(lineno)d - ' \
                       '%(funcName)10s() ]: %(message)s'


@pytest.mark.parametrize("level_logger", [VQDirectStdLevelLogger, VQDirectAllLevelLogger])
@pytest.mark.parametrize("logger_impl", [DirectAllLevelLoggerImpl])
def test_std_level_logger(level_logger, logger_impl):
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger(f"{level_logger.__qualname__}/{logger_impl.__qualname__}")
    log.addHandler(sh)
    log.setLevel(logging.DEBUG)
    logger = VQDirectStdLevelLogger(logger_impl(log))
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


@pytest.mark.parametrize("level_logger, logger_impl", [(VQDirectAllLevelLogger, DirectAllLevelLoggerImpl)])
def test_all_initial_logging(level_logger, logger_impl):
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger(f"{level_logger.__qualname__}/{logger_impl.__qualname__}")
    log.addHandler(sh)
    log.setLevel(TRACE_LOG_LEVEL)
    logger = level_logger(logger_impl(log))
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
