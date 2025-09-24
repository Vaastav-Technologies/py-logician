"""
Tests for main.py file.
"""
import pytest

from logician.main import cli


class TestCLI:
    class TestErrs:
        @pytest.mark.parametrize("cmd_list", [
            [],
            ["-l"],
            ["--list"],
            ["-e"],
            ["--env-list"],
            ["-le"],
            ["-le", "--fmt"],
            ["-le", "--fmt", "{name}"],
            ["-le", "--format", "{name}"]
        ])
        def test_no_command_supplied(self, cmd_list: list[str], capsys):
            with pytest.raises(SystemExit, match="2"):
                cli(cmd_list)
            stderr = capsys.readouterr().err
            assert "error: the following arguments are required: command" in stderr

        @pytest.mark.parametrize("cmd_list", [
            ["cmd-1", "--format={name}"],
            ["cmd-1", "cmd-2", "--fmt"],
            ["cmd-1", "--format"],
            ["cmd-1", "-e", "--fmt"],
            ["cmd-1", "cmd-2", "cmd-3", "--env-list", "--format"],
        ])
        def test_format_without_list(self, cmd_list: list[str], capsys):
            with pytest.raises(SystemExit, match="2"):
                cli(cmd_list)
            stderr = capsys.readouterr().err
            assert "error: --format is only allowed with --list" in stderr
