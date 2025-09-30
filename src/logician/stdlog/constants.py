#!/usr/bin/env python3
# coding=utf-8

"""
Constants related to logging implementation by the python standard logging.
"""

import logging

LOG_LVL = int
"""
Python stdlog level type.

E.g. 10 or logging.DEBUG
"""

LOG_STR_LVL = str
"""
Python stdlog str level type.

E.g. "WARNING"
"""

type EX_LOG_LVL = LOG_LVL | LOG_STR_LVL
"""
Extended log level type.

Extended Type Var for python standard logger logging level.

E.g. logging.DEBUG->"DEBUG"
"""

LOG_FMT = str
"""
Python stdlog logger format type.

E.g. "%(name)s -- %(message)s"
"""

DEFAULT_STACK_LEVEL = 2
"""
``2`` chosen as value because the classes that use this constant actually delegate logging to a user supplied 
underlying_logger. The underlying_logger uses stacklevel=1 to get the 
immediate calling stack, i.e. function, source, filename, lineno, etc of the immediate caller of the log method as in
log.debug(). But when this is delegated by another class (log-capturing-class) to underlying std logger then the 
source information of the log-capturing-class is preferred as that is stacklevel=1, which we do not want. We want that
the source information of the caller-class must be shown. This is just one level up in the calling stack hence, 
stacklevel=DEFAULT_STACK_LEVEL=2 is chosen.


Illustration for ``stacklevel=1``
---------------------------------

    log_caller_src.py :: log.info('info msg') -> log_capturing_class.py :: self.underlying_logger.info('info msg')
    
Prints ::

    log_capturing_class.py | INFO | underlying_logger.info | info msg


Illustration for ``stacklevel=2``
---------------------------------

    log_caller_src.py :: log.info('info msg') -> log_capturing_class.py :: self.underlying_logger.info('info msg')
    
Prints ::

    log_caller_class.py | INFO | calling_meth | info msg

"""


INDIRECTION_STACK_LEVEL = DEFAULT_STACK_LEVEL + 1
"""
Just one more level up on the stack for checking logs.

see DEFAULT_STACK_LEVEL for more details on this.
"""

TRACE_LOG_LEVEL = logging.DEBUG - 5
TRACE_LOG_STR = "TRACE"

SUCCESS_LOG_LEVEL = logging.INFO + 3  # 23
SUCCESS_LOG_STR = "SUCCESS"

NOTICE_LOG_LEVEL = SUCCESS_LOG_LEVEL + 3  # 26
NOTICE_LOG_STR = "NOTICE"

CMD_LOG_LEVEL = NOTICE_LOG_LEVEL + 2  # 28, next level at 30 -> WARNING
CMD_LOG_STR = "COMMAND"

EXCEPTION_TRACEBACK_LOG_LEVEL = TRACE_LOG_LEVEL - 2
"""
Exception traces should only be printed when the user really wants to dig deep into the code and hence should have
very low log level
"""
EXCEPTION_TRACEBACK_LOG_STR = "TRACEBACK"

FATAL_LOG_LEVEL = logging.CRITICAL + 10
FATAL_LOG_STR = "FATAL"
SHORTER_LOG_FMT = "%(levelname)s: %(message)s"
SHORT_LOG_FMT = "%(name)s: %(levelname)s: %(message)s"
DETAIL_LOG_FMT = (
    "%(name)s: %(levelname)s: [%(filename)s - %(funcName)10s() ]: %(message)s"
)
TIMED_DETAIL_LOG_FMT = (
    "%(asctime)s: %(name)s: %(levelname)s: [%(filename)s:%(lineno)d - "
    "%(funcName)10s() ]: %(message)s"
)

WARNING_LEVEL: LOG_LVL = logging.WARNING
"""
Default logging level for the python std lib.
"""
