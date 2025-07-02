#!/usr/bin/env python3
# coding=utf-8

"""
Logging implemented by python standard logging.
"""

# region std_log.constants re-exports
from logician.std_log.constants import DEFAULT_STACK_LEVEL as DEFAULT_STACK_LEVEL
from logician.std_log.constants import INDIRECTION_STACK_LEVEL as INDIRECTION_STACK_LEVEL
from logician.std_log.constants import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from logician.std_log.constants import TRACE_LOG_STR as TRACE_LOG_STR
from logician.std_log.constants import SUCCESS_LOG_LEVEL as SUCCESS_LOG_LEVEL
from logician.std_log.constants import SUCCESS_LOG_STR as SUCCESS_LOG_STR
from logician.std_log.constants import NOTICE_LOG_LEVEL as NOTICE_LOG_LEVEL
from logician.std_log.constants import NOTICE_LOG_STR as NOTICE_LOG_STR
from logician.std_log.constants import CMD_LOG_LEVEL as CMD_LOG_LEVEL
from logician.std_log.constants import CMD_LOG_STR as CMD_LOG_STR
from logician.std_log.constants import EXCEPTION_TRACEBACK_LOG_LEVEL as EXCEPTION_TRACEBACK_LOG_LEVEL
from logician.std_log.constants import EXCEPTION_TRACEBACK_LOG_STR as EXCEPTION_TRACEBACK_LOG_STR
from logician.std_log.constants import FATAL_LOG_LEVEL as FATAL_LOG_LEVEL
from logician.std_log.constants import FATAL_LOG_STR as FATAL_LOG_STR
from logician.std_log.constants import SHORTER_LOG_FMT as SHORTER_LOG_FMT
from logician.std_log.constants import SHORT_LOG_FMT as SHORT_LOG_FMT
from logician.std_log.constants import DETAIL_LOG_FMT as DETAIL_LOG_FMT
from logician.std_log.constants import TIMED_DETAIL_LOG_FMT as TIMED_DETAIL_LOG_FMT
from logician.std_log.constants import WARNING_LEVEL as WARNING_LEVEL
# endregion

# region std_log.base re-exports
from logician.std_log.base import StdLevelLogger as StdLevelLogger
from logician.std_log.base import StdLogProtocol as StdLogProtocol
from logician.std_log.base import DirectStdAllLevelLogger as DirectStdAllLevelLogger
# endregion

# region std_log.all_levels re-exports
from logician.std_log.all_levels import StdProtocolAllLevelLogger as StdProtocolAllLevelLogger
from logician.std_log.all_levels import BaseDirectStdAllLevelLogger as BaseDirectStdAllLevelLogger
from logician.std_log.all_levels import DirectAllLevelLogger as DirectAllLevelLogger
# endregion
