#!/usr/bin/env python3

"""
Configurators for python std logger handlers.
"""

import logging
from abc import abstractmethod
from typing import Protocol, IO, override

from logician.formatters import LogLevelFmt
from logician.stdlog.utils import form_stream_handlers_map, add_new_formatter
from logician.stdlog.constants import LOG_LVL as L, LOG_FMT as F


class HandlerConfigurator(Protocol):
    """
    Configure python stdlog's handlers.
    """

    @abstractmethod
    def configure(
        self,
        level: L,
        logger: logging.Logger,
        stream_fmt_map: dict[IO, LogLevelFmt[L, F]],
    ) -> None:
        """
        Logger handler's configurator.

        Configure the logger's handlers from a user supplied stream-fmt-map.

        :param level: L logging level.
        :param logger: the logger to configure.
        :param stream_fmt_map: the stream-format-handler-map that will configure the supplied logger's handlers.
        """
        pass  # pragma: no cover


class SimpleHandlerConfigurator(HandlerConfigurator):
    """
    Handler configurator that configures loggers' handlers using following rules:

    * Only have ``NullHandler`` in the logger if the supplied ``stream_fmt_map`` is empty. Supplying an empty
      ``stream_fmt_map`` shows the intent of the user to not log to any stream.
    * Add a ``StreamHandler`` for the stream that is provided in ``stream_fmt_map`` but is not present in the logger's
      handlers.
    * If handlers are already present and configured for a stream in logger then simply configure the first handler to
      conform to the supplied stream in the ``stream_fmt_map``.
    """

    @override
    def configure(
        self, level: L, logger: logging.Logger, stream_fmt_map: dict[IO, LogLevelFmt]
    ) -> None:
        """
        Logger handler's configurator.

        Configure the logger's handlers from a user supplied stream-fmt-map.

        >>> import sys
        >>> from logician.stdlog.formatters import StdLogAllLevelSameFmt

          * This configurator removes all the handlers if the supplied ``stream_fmt_map`` is empty {} or Falsy:

            * ``NullHandler`` remains to ensure that no logging is performed. User can specify their intent to not log by
              supplying ``stream_fmt_map`` as empty. This does not ``disable`` the logger, per se, just does not let it
              log to a stream.

            >>> lgr1 = logging.getLogger("lgr1")
            >>> SimpleHandlerConfigurator().configure(logging.INFO, lgr1,
            ...     {})      # empty stream_fmt_map to remove any handlers from lgr
            >>> assert isinstance(lgr1.handlers[0], logging.NullHandler)   # only NullHandler remains

          * Stream handler is added if handlers are not already present for a stream:

            >>> lgr2 = logging.getLogger("lgr2") # no handlers present for STDOUT stream by default
            >>> SimpleHandlerConfigurator().configure(logging.DEBUG, lgr2, {sys.stdout: StdLogAllLevelSameFmt()})  # configure and add handler for STDOUT stream
            >>> str_hn_map = form_stream_handlers_map(lgr2) # for the new stream->list[handlers] map
            >>> assert sys.stdout in str_hn_map # handler introduced for the STDOUT stream

          * Updates the first handler of a stream when the stream is supplied in the ``stream_fmt_map`` and logger already
            has a configured handler for that stream:

            >>> lgr2_1 = logging.getLogger("lgr2") # obtain lgr2 instance as it already has one STDOUT stream->handler configured from before
            >>> new_stdout_handler = logging.StreamHandler(sys.stdout)
            >>> lgr2_1.addHandler(new_stdout_handler) # add another handler for STDOUT stream
            >>> SimpleHandlerConfigurator().configure(logging.DEBUG, lgr2_1, {sys.stdout: StdLogAllLevelSameFmt("%(name)s")})
            >>> str_hn_map = form_stream_handlers_map(lgr2_1) # obtain the updated stream->list[handlers] map
            >>> assert "%(name)s" == str_hn_map[sys.stdout][0].formatter._fmt # type: ignore[attr-defined] only the 0th handler is configured

        :param level: L logging level.
        :param logger: the logger to configure.
        :param stream_fmt_map: the stream-format-handler-map that will configure the supplied logger's handlers.
        """

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
                fmt = lvl_fmt_handlr.fmt(level)  # obtain format for the required level
                if (
                    stream in stream_handlers_map
                ):  # handler already present for the current stream, as stream -> list[handler]
                    if stream_handlers_map[
                        stream
                    ]:  # handlers are already configured for this stream, as stream -> [handler1, handler2, ..., handlerN]
                        handlr = stream_handlers_map[stream][0]  # get the first handler
                        if handlr.formatter:  # handler already has a formatter
                            handlr.formatter._fmt = fmt
                        else:  # no formatter configured for the handler
                            handlr.setFormatter(
                                logging.Formatter(fmt=fmt)
                            )  # configure formatter for this handler
                    else:  # no handler configured for the required stream, as stream -> [], empty handler list or no handlers
                        logger.addHandler(add_new_formatter(stream, fmt))
                else:  # handlers not present for the current stream, as no stream->list[handlers] mapping present in the logger
                    # introduce a new handler
                    logger.addHandler(add_new_formatter(stream, fmt))
