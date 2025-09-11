#!/usr/bin/env python3
# coding=utf-8

"""
Logging implemented by python standard logging.
"""

# region stdlog.constants re-exports
from logician.stdlog.constants import DEFAULT_STACK_LEVEL as DEFAULT_STACK_LEVEL
from logician.stdlog.constants import INDIRECTION_STACK_LEVEL as INDIRECTION_STACK_LEVEL
from logician.stdlog.constants import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from logician.stdlog.constants import TRACE_LOG_STR as TRACE_LOG_STR
from logician.stdlog.constants import SUCCESS_LOG_LEVEL as SUCCESS_LOG_LEVEL
from logician.stdlog.constants import SUCCESS_LOG_STR as SUCCESS_LOG_STR
from logician.stdlog.constants import NOTICE_LOG_LEVEL as NOTICE_LOG_LEVEL
from logician.stdlog.constants import NOTICE_LOG_STR as NOTICE_LOG_STR
from logician.stdlog.constants import CMD_LOG_LEVEL as CMD_LOG_LEVEL
from logician.stdlog.constants import CMD_LOG_STR as CMD_LOG_STR
from logician.stdlog.constants import (
    EXCEPTION_TRACEBACK_LOG_LEVEL as EXCEPTION_TRACEBACK_LOG_LEVEL,
)
from logician.stdlog.constants import (
    EXCEPTION_TRACEBACK_LOG_STR as EXCEPTION_TRACEBACK_LOG_STR,
)
from logician.stdlog.constants import FATAL_LOG_LEVEL as FATAL_LOG_LEVEL
from logician.stdlog.constants import FATAL_LOG_STR as FATAL_LOG_STR
from logician.stdlog.constants import SHORTER_LOG_FMT as SHORTER_LOG_FMT
from logician.stdlog.constants import SHORT_LOG_FMT as SHORT_LOG_FMT
from logician.stdlog.constants import DETAIL_LOG_FMT as DETAIL_LOG_FMT
from logician.stdlog.constants import TIMED_DETAIL_LOG_FMT as TIMED_DETAIL_LOG_FMT
from logician.stdlog.constants import WARNING_LEVEL as WARNING_LEVEL
# endregion

# region stdlog.base re-exports
from logician.stdlog.base import StdLevelLogger as StdLevelLogger
from logician.stdlog.base import StdLogProtocol as StdLogProtocol
from logician.stdlog.base import DirectStdAllLevelLogger as DirectStdAllLevelLogger
# endregion

# region stdlog.all_levels re-exports
from logician.stdlog.all_levels import (
    StdProtocolAllLevelLogger as StdProtocolAllLevelLogger,
)
from logician.stdlog.all_levels import (
    BaseDirectStdAllLevelLogger as BaseDirectStdAllLevelLogger,
)
from logician.stdlog.all_levels import DirectAllLevelLogger as DirectAllLevelLogger
# endregion
