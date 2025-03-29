import logging

import pytest

from vt.utils.logging.logging.std_log.basic_logger_impl import DirectStdLevelLoggerImpl, DirectAllLevelLoggerImpl
from vt.utils.logging.logging.std_log.basic_logger import ProtocolStdLevelLogger, BaseDirectStdLevelLogger

TIMED_DETAIL_LOG_FMT = '%(asctime)s: %(name)s: [%(levelname)s]: [%(filename)s:%(lineno)d - ' \
                       '%(funcName)10s() ]: %(message)s'


@pytest.mark.parametrize("level_logger", [ProtocolStdLevelLogger, BaseDirectStdLevelLogger])
@pytest.mark.parametrize("logger_impl", [DirectStdLevelLoggerImpl, DirectAllLevelLoggerImpl])
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
