#!/usr/bin/env python3
# coding=utf-8

"""
Tests std log configurators.
"""
import logging
import sys
import warnings
from collections import namedtuple
from typing import TextIO
from unittest.mock import patch

import pytest

from vt.utils.logging.logging import DirectAllLevelLogger
from vt.utils.logging.logging.std_log.configurator import StdLoggerConfigurator
from vt.utils.logging.logging.std_log.formatters import StdLogAllLevelSameFmt, \
    StdLogAllLevelDiffFmt
from vt.utils.logging.logging.std_log.formatters import STDERR_ALL_LVL_SAME_FMT
from vt.utils.logging.logging.std_log.utils import level_name_mapping

BOGUS_LEVELS = ['BOGUS', 'bogus', 'non -lev']
LEVEL_NAME_MAPS = [
    None,
    {logging.DEBUG: 'YO-LEVEL'},
    {logging.INFO: 'ANO-INFO', logging.ERROR: 'ANO-ERROR'},
    {28: 'ANO-CMD', 80: '80-LVL', 90: 'NINETY-LVL'}
]

class TestStdLoggerConfigurator:
    class TestArgs:
        class TestStreamMapperNotAllowed:
            @pytest.mark.parametrize('diff', [True, False])
            def test_with_diff_fmt(self, diff):
                with pytest.raises(ValueError, match="Cannot provide both 'stream_fmt_mapper' and "
                                                     "'diff_fmt_per_level'. Choose one."):
                    StdLoggerConfigurator(stream_fmt_mapper=STDERR_ALL_LVL_SAME_FMT, diff_fmt_per_level=diff) # noqa

            @pytest.mark.parametrize('stream_list', [[sys.stderr], [sys.stderr, sys.stdout]])
            def test_with_stream_list(self, stream_list):
                with pytest.raises(ValueError, match="Cannot provide both 'stream_fmt_mapper' and "
                                                     "'stream_list'. Choose one."):
                    StdLoggerConfigurator(stream_fmt_mapper=STDERR_ALL_LVL_SAME_FMT, stream_list=stream_list) # noqa

        class TestStreamList:
            def test_default_produces_stream_formatter_list(self):
                cfg = StdLoggerConfigurator()
                assert sys.stderr in cfg.stream_list

            @pytest.mark.parametrize('stream_list', [[sys.stderr], [sys.stderr, sys.stdout], [sys.stdout, TextIO()]])
            def test_supplied_stream_is_stored(self, stream_list):
                cfg = StdLoggerConfigurator(stream_list=stream_list)
                assert all(stream in cfg.stream_list for stream in stream_list)

            def test_stream_list_from_stream_formatter_mapper_keys(self):
                stream_fmt_mapper={sys.stderr: StdLogAllLevelSameFmt(), sys.stdout: StdLogAllLevelDiffFmt()}
                cfg = StdLoggerConfigurator(stream_fmt_mapper=stream_fmt_mapper)
                assert all(stream in cfg.stream_list for stream in stream_fmt_mapper.keys() )
                assert TextIO not in cfg.stream_list

        class TestStreamFormatMapper:
            def test_defaults_to_std_stream_fmt(self):
                cfg = StdLoggerConfigurator()
                assert cfg.stream_fmt_mapper is not None
                assert cfg.stream_fmt_mapper
                assert isinstance(cfg.stream_fmt_mapper, dict)

            def test_supplied_is_stored(self):
                map_dict = {sys.stderr: StdLogAllLevelSameFmt(), sys.stdout: StdLogAllLevelDiffFmt()}
                cfg = StdLoggerConfigurator(stream_fmt_mapper=map_dict)
                assert cfg.stream_fmt_mapper == map_dict

            @pytest.mark.parametrize("diff, lvl", [(False, StdLogAllLevelSameFmt), (True, StdLogAllLevelDiffFmt)])
            def test_diff_format_stored_when_arg_supplied(self, diff, lvl):
                cfg = StdLoggerConfigurator(diff_fmt_per_level=diff)
                assert all(isinstance(all_lvl_same_fmt, lvl)
                           for all_lvl_same_fmt in cfg.stream_fmt_mapper.values())

    class TestConfigureMethod:
        @pytest.mark.parametrize('level_name_map', [None, {logging.DEBUG: 'YO-LEVEL'},
                                                    {logging.INFO: 'ANO-INFO', logging.ERROR: 'ANO-ERROR'},
                                                    {28: 'ANO-CMD', 80: '80-LVL', 90: 'NINETY-LVL'}])
        def test_supplied_levels_are_registered(self, level_name_map, request):
            """
            All the levels are registered in the logger.

            :param request: required because we want all logger names to be different. This can be achieved using the
                ``request.node.name`` attribute, which gives logger names as
                test_levels_are_registered[level_name_map1], test_levels_are_registered[level_name_map2], ...
            """
            logger_name = request.node.name
            cfg = StdLoggerConfigurator(level_name_map=level_name_map)
            assert cfg.level_name_map == level_name_map
            method = DirectAllLevelLogger.register_levels
            with patch(f"{method.__module__}.{method.__qualname__}") as mocked_fn:
                cfg.configure(logging.getLogger(logger_name))
                mocked_fn.assert_called_once_with(level_name_map)

        @pytest.mark.parametrize('level', [logging.DEBUG, 'INFO', 'COMMAND', logging.ERROR, logging.FATAL, 'TRACEBACK'])
        def test_registers_correctly_given_levels(self, level):
            cfg = StdLoggerConfigurator(level=level)
            log = logging.getLogger(f"correct-given-level-{level}")
            logger = cfg.configure(log)
            if isinstance(level, str):
                int_level = logging.getLevelNamesMapping()[level]
            else:
                int_level = level
            assert logger.underlying_logger.level == int_level
            assert logger.level == int_level

        class TestWarnings:
            @pytest.fixture(params=[(level, level_name_map) for level in BOGUS_LEVELS for level_name_map in LEVEL_NAME_MAPS],
                            scope="function")
            def lvl_fixture(self, request):
                level, level_name_map = request.param
                LvlPackage = namedtuple("LvlPackage", "level, level_name_map")
                return LvlPackage(level, level_name_map)

            def test_warns_on_incorrectly_given_levels(self, lvl_fixture, request):
                level = lvl_fixture.level
                level_name_map = lvl_fixture.level_name_map
                cfg = StdLoggerConfigurator(level=level, level_name_map=level_name_map)
                logger_name = request.node.name
                log = logging.getLogger(logger_name)
                with pytest.warns() as warn_recs:
                    logger = cfg.configure(log)
                levels_to_choose_from: dict[int, str] = level_name_mapping()
                assert len(warn_recs) == 2 # 2 warnings raised
                assert all(w.category == UserWarning for w in warn_recs)
                assert warn_recs[0].message.args[0] == f"{logger.name}: Undefined log level '{level}'. "\
                                                f"Choose from {list(levels_to_choose_from.values())}."
                assert warn_recs[1].message.args[0] == f"{logger.name}: Setting log level to default: "\
                                                       f"'{logging.getLevelName(StdLoggerConfigurator.WARNING_LOG_LEVEL)}'."
                assert logger.underlying_logger.level == StdLoggerConfigurator.WARNING_LOG_LEVEL

            def test_no_warn_on_incorrectly_given_levels_when_no_warn(self, lvl_fixture, request):
                level = lvl_fixture.level
                level_name_map = lvl_fixture.level_name_map
                cfg = StdLoggerConfigurator(level=level, level_name_map=level_name_map, no_warn=True)
                logger_name = request.node.name
                log = logging.getLogger(logger_name)
                with warnings.catch_warnings():
                    warnings.simplefilter("error")
                    logger = cfg.configure(log)
                assert logger.underlying_logger.level == StdLoggerConfigurator.WARNING_LOG_LEVEL

            @pytest.mark.parametrize('no_warn', [True, False])
            def test_sets_default_level_on_when_bogus_level_provided(self, lvl_fixture, request, no_warn):
                level = lvl_fixture.level
                level_name_map = lvl_fixture.level_name_map
                cfg = StdLoggerConfigurator(level=level, level_name_map=level_name_map, no_warn=no_warn)
                logger_name = request.node.name
                log = logging.getLogger(logger_name)
                if no_warn:
                    logger = cfg.configure(log)
                else:
                    with pytest.warns():
                        logger = cfg.configure(log)
                assert logger.underlying_logger.level == StdLoggerConfigurator.WARNING_LOG_LEVEL
