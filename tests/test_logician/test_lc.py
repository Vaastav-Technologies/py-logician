#!/usr/bin/env python3
# coding=utf-8


"""
Test logger configurator for its logging capabilities.
"""
import logging

from logician.stdlog.configurator import StdLoggerConfigurator


class TestStdLogLC:
    """
    Test StdLoggerConfigurator.
    """

    def test_cmd_log_lvl_wo_lvl_supplied(self, capsys):
        """
        Printing cmd log msg without command log level.
        """
        _lgr = logging.getLogger("l-cmd-1")
        lc = StdLoggerConfigurator(level=logging.DEBUG)
        lgr = lc.configure(_lgr)
        lgr.cmd("a msg: %s", "the msg")

    def test_cmd_log_lvl_with_lvl_supplied(self, capsys):
        """
        Printing cmd log msg with command log level.
        """
        _lgr = logging.getLogger("l-cmd-1")
        lc = StdLoggerConfigurator(level=logging.DEBUG)
        lgr = lc.configure(_lgr)
        lgr.cmd("a msg op: %s", "the op", cmd_name="OUT")
