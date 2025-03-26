from vt.utils.logging.std_log.std_log import BasicStdLevelLogger
import logging

TIMED_DETAIL_LOG_FMT = '%(asctime)s: %(name)s: [%(levelname)s]: [%(filename)s:%(lineno)d - ' \
                       '%(funcName)10s() ]: %(message)s'

def test_initial_logging():
    logging.basicConfig()
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(fmt=TIMED_DETAIL_LOG_FMT))
    log = logging.getLogger('init.logging')
    log.addHandler(sh)
    logger = BasicStdLevelLogger(log)
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')
