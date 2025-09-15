#!/usr/bin/env python3
# coding=utf-8


"""
Mappers for

IO-streams -> log-level-format

refer ``logician.formatters.LogLevelFmt`` for log-level-format.
"""

from abc import abstractmethod
from typing import Protocol, IO

from logician.formatters import LogLevelFmt


class StreamFormatMapperComputer[L, F](Protocol):
    """
    Interface for the strategies that can compute and then generate mappings of stream -> level-format-mapper.

    level-format-map - see ``logician.formatters.LogLevelFmt``.

    L - type of ``level`` of the logger, e.g. ``int`` for python std log, like, 10 or logging.DEBUG

    F – type of the returned format, e.g. ``str`` for python std log, like "%(name)s - %(message)s"
    """

    @abstractmethod
    def compute(
        self, same_fmt_per_lvl: F | bool | None, stream_set: set[IO] | None
    ) -> dict[IO, LogLevelFmt[L, F]]:
        """
        Compute the stream format mapper from supplied arguments.

        :param same_fmt_per_lvl: Want same format per logging level?
        :param stream_set: Set of streams this format configuration is to be applied to. Note that ``{}`` denoting an
            empty stream_set is accepted and specifies the user's intent of not logging to any stream.
        :return: a dictionary of stream->log-level-format.
        """

        pass  # pragma: no cover
