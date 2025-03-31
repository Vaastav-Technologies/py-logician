#!/usr/bin/env python3
# coding=utf-8


from vt.utils.logging.logging import BaseDirectStdLevelLogger, BaseDirectAllLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import BaseDirectStdLevelLoggerImpl, \
    BaseDirectAllLevelLoggerImpl
from vt.utils.logging.logging.vq import VerboseQuietLogger


class VQDirectStdLogger(BaseDirectStdLevelLogger, VerboseQuietLogger):
    def __init__(self, logger_impl: BaseDirectStdLevelLoggerImpl):
        super().__init__(logger_impl)
        self._verbosity = None
        self._quietness = None

    def log_fmt(self, temp_verbosity: int | None = None, temp_quietness: int | None = None) -> str:
        return ''

    def set_log_level_vq(self, verbosity: int | None = None, quietness: int | None = None) -> None:
        pass

    @property
    def verbosity(self) -> int | None:
        return self._verbosity

    @property
    def quietness(self) -> int | None:
        return self._quietness


class VQDirectStdLevelLogger(VQDirectStdLogger):
    def __init__(self, logger_impl: BaseDirectStdLevelLoggerImpl):
        super().__init__(logger_impl)


class VQDirectAllLevelLogger(VQDirectStdLogger, BaseDirectAllLevelLogger):
    def __init__(self, logger_impl: BaseDirectAllLevelLoggerImpl):
        super().__init__(logger_impl)
