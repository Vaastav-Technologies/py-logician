#!/usr/bin/env python3
# coding=utf-8

"""
Constants related to logging implementation by the python standard logging.
"""


DEFAULT_STACK_LEVEL = 2
"""
``2`` chosen as value because the classes that use this constant (e.g. vt.utils.logging.std_log.std_log.BasicStdLevelLogger)
actually delegate logging to a user supplied underlying_logger. The underlying_logger uses stacklevel=1 to get the 
immediate calling stack, i.e. function, source, filename, lineno, etc of the immediate caller of the log method as in
log.debug(). But when this is delegated by another class (log-capturing-class) to underlying std logger then the 
source information of the log-capturing-class is preferred as that is stacklevel=1, which we do not want. We want that
the source information of the caller-class must be shown. This is just one level up in the calling stack hence, 
stacklevel=DEFAULT_STACK_LEVEL=2 is chosen.


Illustration for ``stacklevel=1``
---------------------------------

    log_caller_src.py :: log.info('info msg') -> log_capturing_class.py :: self.underlying_logger.info('info msg')
    
Prints ::

    log_capturing_class.py | INFO | undelrying_logger.info | info msg


Illustration for ``stacklevel=2``
---------------------------------

    log_caller_src.py :: log.info('info msg') -> log_capturing_class.py :: self.underlying_logger.info('info msg')
    
Prints ::

    log_caller_class.py | INFO | callling_meth | info msg

"""


INDIRECTION_STACK_LEVEL = DEFAULT_STACK_LEVEL + 1
"""
``3`` chosen as value because the classes that use this constant (e.g. vt.utils.logging.std_log.std_log.BasicStdLevelLogger)
actually delegate logging to a user supplied underlying_logger. The underlying_logger uses stacklevel=1 to get the 
immediate calling stack, i.e. function, source, filename, lineno, etc of the immediate caller of the log method as in
log.debug(). But when this is delegated by another class (log-capturing-class) to underlying std logger then the 
source information of the log-capturing-class is preferred as that is stacklevel=2, which we do not want. We want that
the source information of the caller-class must be shown. This is just one level up in the calling stack hence, 
stacklevel=DEFAULT_STACK_LEVEL+=3 is chosen.


Illustration for ``stacklevel=1``
---------------------------------

    log_caller_src.py :: log.info('info msg') -> log_capturing_class.py :: self.underlying_logger.info('info msg')
    
Prints ::

    log_capturing_class.py | INFO | undelrying_logger.info | info msg


Illustration for ``stacklevel=2``
---------------------------------

    log_caller_src.py :: log.info('info msg') -> log_capturing_class.py :: self.underlying_logger.info('info msg')
    
Prints ::

    log_caller_class.py | INFO | callling_meth | info msg

"""

TRACE_LOG_LEVEL = 5
TRACE_LOG_STR = 'TRACE'

SUCCESS_LOG_LEVEL = 25
SUCCESS_LOG_STR = 'SUCCESS'

NOTICE_LOG_LEVEL = 27
NOTICE_LOG_STR = 'NOTICE'
