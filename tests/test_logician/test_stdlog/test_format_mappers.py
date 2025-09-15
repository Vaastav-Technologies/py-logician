#!/usr/bin/env python3
# coding=utf-8

"""
Tests related to format-mappers computers of stdlog.
"""

import logging
import sys
from typing import TextIO

import pytest

from logician.stdlog.format_mappers import StdStrFmtMprComputer
from logician.stdlog.formatters import StdLogAllLevelSameFmt, StdLogAllLevelDiffFmt


class TestStdStrFmtMprComputer:
    """
    Tests for ``StdStrFmtMprComputer.compute()`` method.
    """

    @pytest.fixture()
    def sut(self) -> StdStrFmtMprComputer:
        """
        System Under Test.

        :return: instance of ``StdStrFmtMprComputer``.
        """
        return StdStrFmtMprComputer()

    @pytest.mark.parametrize(
        "same_fmt_per_lvl",
        [
            None,
            True,
            False,
            "%(levelname)s -- %(message)s",
            5,  # 5 or int is not a valid value for this function. Included here just for completeness.
        ],
    )
    def test_empty_dict_when_stream_set_is_empty(self, same_fmt_per_lvl, sut):
        """
        Always returns empty dict regardless of the value of ``same_fmt_per_lvl`` if ``stream_set`` is an empty set.
        """
        assert sut.compute(same_fmt_per_lvl, set()) == {}

    class TestStreamSetIsNone:
        @pytest.mark.parametrize(
            "same_fmt_per_lvl",
            [
                None,
                True,
                False,
                "%(levelname)s -- %(message)s",
                5,
                # 5 or int is not a valid value for this function. Included here just for completeness.
            ],
        )
        def test_only_stderr_stream_present(self, same_fmt_per_lvl, sut):
            ret_dict = sut.compute(same_fmt_per_lvl, None)
            assert len(ret_dict) == 1
            assert sys.stderr in ret_dict

        @pytest.mark.parametrize("same_fmt_per_lvl", [None, False, "", 0])
        class TestSameFmtPerLevelIsFalsy:
            """
            ``same_fmt_per_lvl`` is ``False`` or ``None``.
            """

            def test_only_stderr_stream_present(self, same_fmt_per_lvl, sut):
                """
                Only stderr present.
                """
                ret_dict = sut.compute(same_fmt_per_lvl, None)
                assert len(ret_dict) == 1
                assert sys.stderr in ret_dict

            def test_stderr_stream_present_with_diff_fmt(self, same_fmt_per_lvl, sut):
                """
                stderr present with all levels diff fmt.
                """
                ret_dict = sut.compute(same_fmt_per_lvl, None)
                assert isinstance(ret_dict[sys.stderr], StdLogAllLevelDiffFmt)

        @pytest.mark.parametrize(
            "same_fmt_per_lvl",
            [
                True,
                "%(name)s",
                1,  # not valid value, just for testing purpose
                [1],  # not valid value, just for testing purpose
            ],
        )
        class TestSameFmtPerLevelIsTruthy:
            """
            ``same_fmt_per_lvl`` is truthy.
            """

            def test_only_stderr_stream_present(self, same_fmt_per_lvl, sut):
                """
                only stderr stream is present.
                """
                ret_dict = sut.compute(same_fmt_per_lvl, None)
                assert len(ret_dict) == 1
                assert sys.stderr in ret_dict

            def test_stderr_stream_present_with_same_fmt(self, same_fmt_per_lvl, sut):
                """
                stderr present with all levels same fmt.
                """
                ret_dict = sut.compute(same_fmt_per_lvl, None)
                assert isinstance(ret_dict[sys.stderr], StdLogAllLevelSameFmt)

    @pytest.mark.parametrize(
        "stream_set, same_fmt_per_level, num_entries, fmt_per_lvl",
        [
            ({sys.stderr}, True, 1, StdLogAllLevelSameFmt),
            ({sys.stderr}, False, 1, StdLogAllLevelDiffFmt),
            ({sys.stderr, sys.stdout}, True, 2, StdLogAllLevelSameFmt),
            ({sys.stderr, sys.stdout}, False, 2, StdLogAllLevelDiffFmt),
            ({sys.stderr, sys.stdout}, "%(name)s", 2, StdLogAllLevelSameFmt),
            ({sys.stderr, sys.stdout}, False, 2, StdLogAllLevelDiffFmt),
            ({sys.stderr, sys.stdout}, None, 2, StdLogAllLevelDiffFmt),
        ],
    )
    class TestMultiplePermutations:
        def test_only_supplied_streams_included(
            self, stream_set, same_fmt_per_level, num_entries, fmt_per_lvl, sut
        ):
            """
            :param stream_set: the set of streams supplied.
            :param same_fmt_per_level: same format per level?
            :param num_entries: number of entries in the returned dict to verify for assertion.
            :param fmt_per_lvl: fmt per level class to be verified.
            :param sut: system under test
            """
            ret_dict = sut.compute(same_fmt_per_level, stream_set)
            assert len(stream_set) == num_entries
            assert len(ret_dict) == num_entries
            assert all(stream in ret_dict for stream in stream_set)

        def test_format_mappers_are_of_correct_type(
            self, stream_set, same_fmt_per_level, num_entries, fmt_per_lvl, sut
        ):
            """
            :param stream_set: the set of streams supplied.
            :param same_fmt_per_level: same format per level?
            :param num_entries: number of entries in the returned dict to verify for assertion.
            :param fmt_per_lvl: fmt per level class to be verified.
            :param sut: system under test
            """
            ret_dict = sut.compute(same_fmt_per_level, stream_set)
            assert all(isinstance(fpl, fmt_per_lvl) for stream, fpl in ret_dict.items())

    @pytest.mark.parametrize(
        "fmt_per_lvl, stream_set, num_entries",
        [
            ("%(name)s", {sys.stderr}, 1),
            ("%(name)s -- %(message)s", {sys.stderr, sys.stdout}, 2),
            (
                "%(name)s -- %(levelname)s -- %(message)s",
                {sys.stderr, sys.stdout, TextIO()},
                3,
            ),
        ],
    )
    class TestSameFmtPerLevelProvidesFmt:
        """
        Format is actually provided as a string by the ``same_fmt_per_level`` param.

        In this case, all the streams must conform to all-logging-levels-same-format.
        """

        def test_only_provided_streams_exist(
            self, fmt_per_lvl, stream_set, num_entries, sut
        ):
            ret_dict = sut.compute(fmt_per_lvl, stream_set)
            assert len(ret_dict) == num_entries
            assert all(stream in ret_dict for stream in stream_set)

        def test_format_mappers_are_of_correct_type(
            self, fmt_per_lvl, stream_set, num_entries, sut
        ):
            """
            :param stream_set: the set of streams supplied.
            :param fmt_per_lvl: same format per level?
            :param num_entries: number of entries in the returned dict to verify for assertion.
            :param sut: system under test
            """
            ret_dict = sut.compute(fmt_per_lvl, stream_set)
            assert all(
                isinstance(fpl, StdLogAllLevelSameFmt)
                for stream, fpl in ret_dict.items()
            )

        @pytest.mark.parametrize("level", [logging.DEBUG, logging.FATAL])
        def test_format_mappers_have_the_supplied_fmt(
            self, fmt_per_lvl, stream_set, num_entries, level, sut
        ):
            """
            :param stream_set: the set of streams supplied.
            :param fmt_per_lvl: same format per level?
            :param num_entries: number of entries in the returned dict to verify for assertion.
            :param sut: system under test
            """
            ret_dict = sut.compute(fmt_per_lvl, stream_set)
            assert all(
                fpl.fmt(level) == fmt_per_lvl for stream, fpl in ret_dict.items()
            )
