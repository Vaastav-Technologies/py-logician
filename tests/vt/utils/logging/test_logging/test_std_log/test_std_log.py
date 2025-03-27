import logging

import pytest

from vt.utils.logging.logging.std_log.std_log import BasicStdProtocolLevelLogger, BasicStdLevelLogger

TIMED_DETAIL_LOG_FMT = '%(asctime)s: %(name)s: [%(levelname)s]: [%(filename)s:%(lineno)d - ' \
                       '%(funcName)10s() ]: %(message)s'

@pytest.mark.parametrize("level_logger", [BasicStdProtocolLevelLogger, BasicStdLevelLogger])
def test_initial_logging(level_logger):
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger(level_logger.__qualname__)
    log.addHandler(sh)
    log.setLevel(logging.DEBUG)
    logger = level_logger(log) # noqa, IDE known bug: https://stackoverflow.com/a/79009762
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')
    try:
        raise ValueError('A value is wrong.')
    except ValueError:
        logger.exception('an error')
    logger.fatal('fatal message')
