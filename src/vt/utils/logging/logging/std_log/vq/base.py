#!/usr/bin/env python3
# coding=utf-8


from vt.utils.logging.logging import BaseDirectStdAllLevelLogger, BaseDirectAllLevelLogger
from vt.utils.logging.logging.std_log.basic_logger_impl import BaseDirectStdAllLevelLoggerImpl, \
    BaseDirectAllLevelLoggerImpl
from vt.utils.logging.logging.vq import VerboseQuietLogger
from vt.utils.logging.logging.vq import ChangingFormatVQLogger


class VQDirectStdAllLogger(BaseDirectStdAllLevelLogger, VerboseQuietLogger):
    def __init__(self, logger_impl: BaseDirectStdAllLevelLoggerImpl):
        super().__init__(logger_impl)
        self._verbosity = None
        self._quietness = None

    def set_log_level_vq(self, verbosity: int | None = None, quietness: int | None = None) -> None:
        pass

    @property
    def verbosity(self) -> int | None:
        return self._verbosity

    @property
    def quietness(self) -> int | None:
        return self._quietness


class ChangingFmtVQDirectStdLogger(VQDirectStdAllLogger, ChangingFormatVQLogger):

    def log_fmt(self, temp_verbosity: int | None, temp_quietness: int | None) -> str:
        pass


class VQDirectStdLevelLogger(VQDirectStdAllLogger):
    def __init__(self, logger_impl: BaseDirectStdAllLevelLoggerImpl):
        super().__init__(logger_impl)


class VQDirectAllLevelLogger(VQDirectStdAllLogger, BaseDirectAllLevelLogger):
    def __init__(self, logger_impl: BaseDirectAllLevelLoggerImpl):
        super().__init__(logger_impl)
