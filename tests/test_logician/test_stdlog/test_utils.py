#!/usr/bin/env python3

"""
Tests related to logician.stdlog.utils
"""
import logging
import sys

import pytest

from logician.stdlog import SHORTER_LOG_FMT
from logician.stdlog.formatters import StdLogAllLevelSameFmt
from logician.stdlog.utils import simple_handlr_cfgr, form_stream_handlers_map


class TestSimpleHandlerFormatter:
    def test_empty_map_removes_all_handlers(self, request):
        """
        This configurator removes all the handlers if the supplied ``stream_fmt_map`` is empty {} or Falsy

        ``NullHandler`` remains to ensure that no logging is performed. User can specify their intent to not log by
        supplying ``stream_fmt_map`` as empty. This does not ``disable`` the logger, per se, just does not let it
        log to a stream.
        """
        lgr1 = logging.getLogger(request.node.name)
        assert len(lgr1.handlers) >= 0  # there are handlers already configured when logger gets created else logging.lastResort is picked up.
        simple_handlr_cfgr(
            None,  # type: ignore[arg-type] expected int, supplied None
            lgr1,
            {}  # empty stream_fmt_map to remove any handlers from lgr
        )
        assert len(lgr1.handlers) == 1  # only NullHandler remains
        assert isinstance(lgr1.handlers[0], logging.NullHandler)  # only NullHandler remains

    def test_handler_added_if_no_handler_configured(self, request):
        """
        Stream handler is added if handlers are not already configured for a stream

        * prepare logger so that no handlers are present for the STDOUT stream.
        * configure STDOUT stream. This adds a handler for the STDOUT stream.
        * verify that the handler is introduced.
        """
        lgr2 = logging.getLogger(request.node.name)
        str_hn_map = form_stream_handlers_map(lgr2)
        assert sys.stdout not in str_hn_map  # no handlers configured for STDOUT stream
        simple_handlr_cfgr(logging.DEBUG, lgr2,
            {sys.stdout: StdLogAllLevelSameFmt()}   # fmt added for STDOUT stream
        )
        str_hn_map = form_stream_handlers_map(lgr2)  # for the new stream->list[handlers] map
        assert sys.stdout in str_hn_map  # handler introduced for the STDOUT stream

    class TestHandlersUpdatedToHaveRightFmt:
        """
        Updates the first handler of a stream when the stream is supplied in the ``stream_fmt_map`` and logger already
        has a configured handler for that stream
        """

        @pytest.fixture(scope="function")
        def stdout_3_handlr_logger(self, request) -> logging.Logger:
            """
            Logger with 3 handlers for STDOUT stream

            * prepare logger. This by default doesn't introduce any handlers for STDOUT stream.
            * configure the logger to include STDOUT stream configuration. This introduces STDOUT stream to the logger.
            * add another handler for STDOUT stream.

            :return: the logger having 3 handlers for STDOUT stream.
            """
            lgr3 = logging.getLogger(request.node.name)
            stdout_handler1 = logging.StreamHandler(sys.stdout)
            stdout_handler1.setFormatter(logging.Formatter(SHORTER_LOG_FMT))    # handler1 has a formatter configured
            lgr3.addHandler(stdout_handler1)
            stdout_handler2 = logging.StreamHandler(sys.stdout)
            lgr3.addHandler(stdout_handler2)  # add another handler for STDOUT stream, this handler has no formatter
            stdout_handler3 = logging.StreamHandler(sys.stdout)
            stdout_handler3.setFormatter(logging.Formatter(SHORTER_LOG_FMT))
            lgr3.addHandler(stdout_handler3)    # handler1 has a formatter configured
            return lgr3

        class TestFixtures:
            """
            Just test all the fixtures provided by this class.
            """
            def test_stdout_3_handlr_logger_has_3_stdout_handlers(self, stdout_3_handlr_logger):
                lgr = stdout_3_handlr_logger
                assert len(lgr.handlers) == 3 # three handlers in total

            def test_str_hn_map_has_3_stdout_handlers(self, stdout_3_handlr_logger):
                lgr = stdout_3_handlr_logger
                str_hn_map = form_stream_handlers_map(lgr)
                assert len(str_hn_map[sys.stdout]) == 3  # now, we have three handlers for STDOUT stream

            def test_doesnt_change_number_of_handlers(self, stdout_3_handlr_logger):
                lgr = stdout_3_handlr_logger
                str_hn_map = form_stream_handlers_map(lgr)
                assert len(str_hn_map[sys.stdout]) == 3  # number of handlers didn't change

        def test_first_handler_updated(self, stdout_3_handlr_logger):
            """
            Only the 0th index handler is updated.

            * now, configuring handler for stdout stream must only affect the first (0th index) attached handler.
            """
            lgr = stdout_3_handlr_logger
            simple_handlr_cfgr(logging.DEBUG, lgr, {sys.stdout: StdLogAllLevelSameFmt("%(name)s")})
            str_hn_map = form_stream_handlers_map(lgr)
            assert "%(name)s" == str_hn_map[sys.stdout][0].formatter._fmt  # type: ignore[attr-defined] 0th handler reconfigured to include the supplied format.

        def test_other_handlers_not_updated(self, stdout_3_handlr_logger):
            """
            No other handler is updated

            * now, configuring handler for stdout stream must not affect any attached handler other than the 0th.
            """
            lgr = stdout_3_handlr_logger
            simple_handlr_cfgr(logging.DEBUG, lgr, {sys.stdout: StdLogAllLevelSameFmt("%(name)s")})
            str_hn_map = form_stream_handlers_map(lgr)
            assert all(
                "%(name)s" != hn.formatter._fmt for hn in str_hn_map[sys.stdout][1:] if hn.formatter)  # type: ignore[attr-defined]

    def test_logger_has_handler_added_but_fmtr_not_configured(self, request):
        """
        Adds the required formatter to the logger's handler if:
            - the handler is already present for the required stream in the logger.
            - and formatter is not already set for that handler.

        * prepare a logger.
        * add a handler for the STDERR stream but do not set any formatter for it.
        * now, ``simple_handlr_cfgr`` adds a formatter for the handler of that stream.
        """
        handler = logging.StreamHandler()   # stderr handler
        assert not handler.formatter    # handler has no formatter set
        lgr4 = logging.getLogger(request.node.name)
        assert not lgr4.handlers    # logger has no handlers for any stream
        lgr4.addHandler(handler)    # add our stderr handler to lgr4, still the handler has no formatter set
        assert handler in lgr4.handlers # our added handler in lgr4's handlers
        assert len(lgr4.handlers) == 1 # only our handler present
        assert not lgr4.handlers[0].formatter  # the present handler has no formatter
        simple_handlr_cfgr(logging.DEBUG, lgr4, {sys.stderr: StdLogAllLevelSameFmt("%(name)s")})
        assert handler in lgr4.handlers # our added handler in lgr4's handlers
        assert len(lgr4.handlers) == 1 # only our handler present
        assert lgr4.handlers[0].formatter  # the present handler has a formatter now
        assert lgr4.handlers[0].formatter._fmt == "%(name)s"    # our supplied format is configured for the formatter
