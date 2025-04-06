#!/usr/bin/env python3
# coding=utf-8

"""
Tests std log configurators.
"""
import sys
from typing import TextIO

import pytest

from vt.utils.logging.logging.std_log.configurator import StdLoggerConfigurator
from vt.utils.logging.logging.std_log.formatters import StdStreamFormatMapper, StdLogAllLevelSameFmt, \
    StdLogAllLevelDiffFmt


class TestStdLoggerConfigurator:
    class TestArgs:
        class TestStreamMapperNotAllowed:
            @pytest.mark.parametrize('diff', [True, False])
            def test_with_diff_fmt(self, diff):
                with pytest.raises(ValueError, match="Cannot provide both 'stream_fmt_mapper' and "
                                                     "'diff_fmt_per_level'. Choose one."):
                    StdLoggerConfigurator(stream_fmt_mapper=StdStreamFormatMapper(), diff_fmt_per_level=diff) # noqa

            @pytest.mark.parametrize('stream_list', [[sys.stderr], [sys.stderr, sys.stdout]])
            def test_with_stream_list(self, stream_list):
                with pytest.raises(ValueError, match="Cannot provide both 'stream_fmt_mapper' and "
                                                     "'stream_list'. Choose one."):
                    StdLoggerConfigurator(stream_fmt_mapper=StdStreamFormatMapper(), stream_list=stream_list) # noqa

    class TestStreamList:
        def test_default_produces_stream_formatter_list(self):
            cfg = StdLoggerConfigurator()
            assert sys.stderr in cfg.stream_list

        @pytest.mark.parametrize('stream_list', [[sys.stderr], [sys.stderr, sys.stdout], [sys.stdout, TextIO()]])
        def test_supplied_stream_is_stored(self, stream_list):
            cfg = StdLoggerConfigurator(stream_list=stream_list)
            assert all(stream in cfg.stream_list for stream in stream_list)

        def test_stream_list_from_stream_formatter_mapper_keys(self):
            stream_fmt_mapper=StdStreamFormatMapper({sys.stderr: StdLogAllLevelSameFmt(),
                                                     sys.stdout: StdLogAllLevelDiffFmt()})
            cfg = StdLoggerConfigurator(stream_fmt_mapper=stream_fmt_mapper)
            assert all(stream in cfg.stream_list for stream in stream_fmt_mapper.stream_fmt_map.keys() )
            assert TextIO not in cfg.stream_list

    class TestStreamFormatMapper:
        def test_defaults_to_std_stream_fmt(self):
            cfg = StdLoggerConfigurator()
            assert cfg.stream_fmt_mapper is not None
            assert cfg.stream_fmt_mapper
            assert isinstance(cfg.stream_fmt_mapper, StdStreamFormatMapper)

        def test_supplied_is_stored(self):
            map_dict = {sys.stderr: StdLogAllLevelSameFmt(),
                        sys.stdout: StdLogAllLevelDiffFmt()}
            mapper = StdStreamFormatMapper(map_dict)
            cfg = StdLoggerConfigurator(stream_fmt_mapper=mapper)
            assert cfg.stream_fmt_mapper == mapper

        @pytest.mark.parametrize("diff, lvl", [(False, StdLogAllLevelSameFmt), (True, StdLogAllLevelDiffFmt)])
        def test_diff_format_stored_when_arg_supplied(self, diff, lvl):
            cfg = StdLoggerConfigurator(diff_fmt_per_level=diff)
            assert all(isinstance(all_lvl_same_fmt, lvl)
                       for all_lvl_same_fmt in cfg.stream_fmt_mapper.stream_fmt_map.values())
