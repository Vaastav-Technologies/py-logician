import logging

from vt.utils.logging.logging.std_log.std_log import BasicStdLevelLogger

TIMED_DETAIL_LOG_FMT = '%(asctime)s: %(name)s: [%(levelname)s]: [%(filename)s:%(lineno)d - ' \
                       '%(funcName)10s() ]: %(message)s'

def test_initial_logging():
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger('init.logging')
    log.addHandler(sh)
    log.setLevel(logging.DEBUG)
    logger = BasicStdLevelLogger(log) # noqa, IDE known bug: https://stackoverflow.com/a/79009762
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
