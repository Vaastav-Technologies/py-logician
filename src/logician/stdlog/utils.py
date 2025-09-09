#!/usr/bin/env python3
# coding=utf-8

"""
Important utilities for std python logging library.
"""
import logging
import sys
from logging import Handler
from typing import TextIO, IO
from collections import defaultdict

from vt.utils.errors.warnings import vt_warn

from logician.formatters import LogLevelFmt
from logician.stdlog.formatters import StdLogAllLevelSameFmt


def level_name_mapping() -> dict[int, str]:
    """
    :return: level -> name mapping from std lib.
    """
    return {level: logging.getLevelName(level) for level in
            sorted(logging.getLevelNamesMapping().values())}


class TempSetLevelName:
    def __init__(self, level: int, level_name: str | None, reverting_lvl_name: str, no_warn: bool = False):
        """
        Set the log level name temporarily and then revert it back to the ``reverting_lvl_name``.

        :param level: The log level to set name to.
        :param level_name: Level name to set the level to.
        :param reverting_lvl_name: The log level name to revert to when operation finishes.
        :param no_warn: A warning is shown if the supplied ``level_name`` is strip-empty. This warning can be suppressed
            by setting ``no_warn=True``.
        """
        self.level = level
        self.level_name = level_name
        self.reverting_lvl_name = reverting_lvl_name
        self.no_warn = no_warn
        self.original_level_name = logging.getLevelName(level)

    def __enter__(self):
        if self.level_name is not None:
            if self.level_name.strip() == '':
                self.warn_user()
            else:
                logging.addLevelName(self.level, self.level_name)

    def warn_user(self):
        """
        A warning is shown if the supplied ``level_name`` is strip-empty. This warning can be suppressed
            by setting ``no_warn=True`` in ctor.
        """
        if not self.no_warn:
            self._warn_user()

    def _warn_user(self):
        vt_warn(f"Supplied log level name for log level {self.level} is empty.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.level_name:
            logging.addLevelName(self.level, self.reverting_lvl_name)
        else:
            logging.addLevelName(self.level, self.original_level_name)


def get_first_non_none[T](lst: list[T | None], default: T | None = None) -> T | None:
    """
    Get first non-``None`` item from the list ``lst`` else ``default``.

    Examples:

      * Return the default if all values are ``None``:

        >>> get_first_non_none([None, None, None], 5)
        5

      * default can be ``None``:

        >>> get_first_non_none([None, None], None)

      * first non-``None`` is returned:

        >>> get_first_non_none([None, None, 2, None, 5], 9)
        2

      * default is returned when empty-list is supplied:

        >>> get_first_non_none([], "some str")
        'some str'

        >>> get_first_non_none([], None) # None returned as default is None

        >>> get_first_non_none([]) # None returned as default is None

    :param lst: list of values.
    :param default: value to return if list consists of all ``None``s.
    :return: first non ``None`` value or ``default`` if all ``None`` are encountered.
    """
    for lst_elem in lst:
        if lst_elem is not None:
            return lst_elem
    return default


def form_stream_handlers_map(logger: logging.Logger) -> dict[IO, list[Handler]]:
    """
    :param logger: the logger whose stream->list[handlers] mapping is to be obtained.
    :return: stream->list[handlers] mapping for the supplied logger.
    """
    stream_handler_map: dict[IO, list[Handler]] = defaultdict(list)
    """
    Map of logger's stream and its handlers.
    """
    # Create a mapping of stream->list[handlers for that stream]
    for handlr in logger.handlers:
        if isinstance(handlr, logging.StreamHandler):
            stream_handler_map[handlr.stream].append(handlr)
    return stream_handler_map


def simple_handlr_cfgr(level: int, logger: logging.Logger, stream_fmt_map: dict[TextIO, LogLevelFmt],
                propagate: bool = False) -> None:
    """
    Logger handler's configurator.

    Configure the logger's handlers from a user supplied stream-fmt-map.

      * This configurator removes all the handlers if the supplied ``stream_fmt_map`` is empty {} or Falsy:

        * ``NullHandler`` remains to ensure that no logging is performed. User can specify their intent to not log by
          supplying ``stream_fmt_map`` as empty.

        >>> def test_empty_map_removes_all_handlers():  # define test
        ...     lgr1 = logging.getLogger("lgr1")
        ...     assert len(lgr1.handlers) >= 0   # there are handlers already configured when logger gets created else logging.lastResort is picked up.
        ...     simple_handlr_cfgr(
        ...         None,   # type: ignore[arg-type] expected int, supplied None
        ...         lgr1,
        ...         {}      # empty stream_fmt_map to remove any handlers from lgr
        ...     )
        ...     assert len(lgr1.handlers) == 1   # only NullHandler remains
        ...     assert isinstance(lgr1.handlers[0], logging.NullHandler)   # only NullHandler remains
        >>> test_empty_map_removes_all_handlers()   # run test

      * Stream handler is added if handlers are not already configured for a stream:

        >>> def test_handler_added_if_no_handler_configured(lgr_name):  # define test
        ...     lgr2 = logging.getLogger(lgr_name)
        ...     str_hn_map = form_stream_handlers_map(lgr2)
        ...     assert sys.stdout not in str_hn_map # no handlers configured for STDOUT stream
        ...     simple_handlr_cfgr(
        ...         logging.DEBUG,
        ...         lgr2,
        ...         {sys.stdout: StdLogAllLevelSameFmt()}
        ...     )
        ...     str_hn_map = form_stream_handlers_map(lgr2) # for the new stream->list[handlers] map
        ...     assert sys.stdout in str_hn_map # handler introduced for the STDOUT stream
        ...     return lgr2
        >>> _ = test_handler_added_if_no_handler_configured("lgr2")   # run test

      * Updates the first handler of a stream when the stream is supplied in the ``stream_fmt_map`` and logger already
        has a configured handler for that stream:

        >>> def test_first_handler_updated():   # define test
        ...     lgr3 = test_handler_added_if_no_handler_configured("lgr3")
        ...     str_hn_map = form_stream_handlers_map(lgr3)
        ...     assert sys.stdout in str_hn_map # handler already configured for STDOUT stream from test_handler_added_if_no_handler_configured()
        ...     assert len(str_hn_map[sys.stdout]) == 1 # only 1 handler configured for STDOUT stream
        ...     new_stdout_handler = logging.StreamHandler(sys.stdout)
        ...     lgr3.addHandler(new_stdout_handler) # add another handler for STDOUT stream
        ...     str_hn_map = form_stream_handlers_map(lgr3)
        ...     assert len(str_hn_map[sys.stdout]) == 2 # now, we have two handlers for STDOUT stream
        ...     simple_handlr_cfgr(
        ...        logging.DEBUG,
        ...        lgr3,
        ...        {sys.stdout: StdLogAllLevelSameFmt("%(name)s")}
        ...     )
        ...     str_hn_map = form_stream_handlers_map(lgr3) # obtain the updated stream->list[handlers] map
        ...     assert len(str_hn_map[sys.stdout]) == 2 # number of handlers didn't change
        ...     assert "%(name)s" == str_hn_map[sys.stdout][0].formatter._fmt # type: ignore[attr-defined]
        ...     ["%(name)s" != hn.formatter._fmt for hn in str_hn_map[sys.stdout]]
        ...     assert all("%(name)s" != hn.formatter._fmt for hn in str_hn_map[sys.stdout][1:]) # type: ignore[attr-defined]
        >>> test_first_handler_updated()

    :param level: int logging level.
    :param logger: the logger to configure.
    :param stream_fmt_map: the stream-format-handler-map that will configure the supplied logger's handlers.
    :param propagate: propagate logger records to parent loggers.
    """

    def new_formatter(_logger, _stream, _fmt, add_handler=True):
        _handlr = logging.StreamHandler(stream=_stream)  # type: ignore[arg-type]
        _handlr.setFormatter(logging.Formatter(fmt=_fmt))
        if add_handler:
            _logger.addHandler(_handlr)
        return _handlr

    logger.propagate = propagate
    if not stream_fmt_map:
        # empty user-supplied stream->formatter map
        # specifies the user's intent to not log anywhere hence, clear all existing handlers
        logger.handlers.clear()
        # add a NullHandler else the logging goes to logging.lastResort
        logger.addHandler(logging.NullHandler())
    else:
        stream_handlers_map = form_stream_handlers_map(logger)
        for stream in stream_fmt_map:
            lvl_fmt_handlr = stream_fmt_map[stream]
            fmt = lvl_fmt_handlr.fmt(level) # obtain format for the required level
            if stream in stream_handlers_map:    # handler already present for the current stream, as stream -> list[handler]
                if stream_handlers_map[stream]: # handlers are already configured for this stream, as stream -> [handler1, handler2, ..., handlerN]
                    handlr = stream_handlers_map[stream][0] # get the first handler
                    if handlr.formatter:    # handler already has a formatter
                        handlr.formatter._fmt = fmt
                    else:   # no formatter configured for the handler
                        handlr.setFormatter(logging.Formatter(fmt=fmt)) # configure formatter for this handler
                else:   # no handler configured for the required stream, as stream -> [], empty handler list or no handlers
                    new_formatter(logger, stream, fmt)
            else:   # handlers not present for the current stream, as no stream->list[handlers] mapping present in the logger
                # introduce a new handler
                new_formatter(logger, stream, fmt)
