#!/usr/bin/env python3
# coding=utf-8


"""
Mappers for python stdlog of

IO-streams -> log-level-format

refer ``logician.stdlog.formatters.StdLogLevelFmt`` for log-level-format.
"""

from abc import abstractmethod
from typing import Protocol, IO, override

from logician.format_mappers import StreamFormatMapperComputer
from logician.stdlog.formatters import (
    StdLogLevelFmt,
    StdLogAllLevelSameFmt,
    StdLogAllLevelDiffFmt,
    STDERR_ALL_LVL_SAME_FMT,
    STDERR_ALL_LVL_DIFF_FMT,
    stderr_all_lvl_same_fmt,
)
from logician.stdlog.constants import LOG_LVL as L, LOG_FMT as F


class StdStreamFormatMapperComputer(StreamFormatMapperComputer[L, F], Protocol):
    """
    Interface for the strategies that can compute and then generate mappings of stream -> level-format-mapper for
    python stdlog.

    level-format-map - see ``logician.stdlog.formatters.StdLogLevelFmt``.
    """

    @override
    @abstractmethod
    def compute(
        self, same_fmt_per_lvl: F | bool | None, stream_set: set[IO] | None
    ) -> dict[IO, StdLogLevelFmt]:
        pass  # pragma: no cover


class StdStrFmtMprComputer(StdStreamFormatMapperComputer):
    """
    Implementation of interface ``StdStreamFormatMapperComputer``.

    >>> import sys
    >>> sut = StdStrFmtMprComputer()

    Follows certain rules:

      * Empty ``stream_set``, like, ``{}`` returns an empty dict:

        >>> assert sut.compute(True, set()) == {}

      * ``same_fmt_per_level`` can set same format for all logging levels.

        >>> ret_dict = sut.compute(True, {sys.stderr})
        >>> assert isinstance(ret_dict[sys.stderr], StdLogAllLevelSameFmt)

      * ``same_fmt_per_level`` can enforce same format for all logging levels.

        >>> ret_dict = sut.compute("%(name)s", {sys.stderr})
        >>> assert isinstance(ret_dict[sys.stderr], StdLogAllLevelSameFmt)
        >>> assert ret_dict[sys.stderr].fmt(10) == "%(name)s"   # any level has same formats

      * ``False`` ``same_fmt_per_level`` results in different logging formats per level.

        >>> ret_dict = sut.compute(False, {sys.stdout, sys.stderr})
        >>> assert isinstance(ret_dict[sys.stderr], StdLogAllLevelDiffFmt)
        >>> assert isinstance(ret_dict[sys.stderr], StdLogAllLevelDiffFmt)

      * ``None`` ``stream_set`` and ``same_fmt_per_level`` enforces different-format-per-log-level on the stderr stream.

        >>> ret_dict = sut.compute(None, None)
        >>> assert len(ret_dict) == 1
        >>> assert sys.stderr in ret_dict   # only one entry of stderr stream present
        >>> assert isinstance(ret_dict[sys.stderr], StdLogAllLevelDiffFmt)
    """

    @override
    def compute(
        self, same_fmt_per_lvl: F | bool | None, stream_set: set[IO] | None
    ) -> dict[IO, StdLogLevelFmt]:
        if stream_set is not None:  # accepts empty stream_set
            if same_fmt_per_lvl:
                if isinstance(same_fmt_per_lvl, F):
                    return {
                        stream: StdLogAllLevelSameFmt(same_fmt_per_lvl)
                        for stream in stream_set
                    }
                return {stream: StdLogAllLevelSameFmt() for stream in stream_set}
            return {stream: StdLogAllLevelDiffFmt() for stream in stream_set}
        else:
            if same_fmt_per_lvl:
                if isinstance(same_fmt_per_lvl, F):
                    return stderr_all_lvl_same_fmt(same_fmt_per_lvl)
                return STDERR_ALL_LVL_SAME_FMT
            return STDERR_ALL_LVL_DIFF_FMT
