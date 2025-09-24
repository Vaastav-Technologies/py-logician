#!/usr/bin/env python3
# coding=utf-8

"""
Extract and showcase details about a program's logger configurators.
"""

import os
import shlex
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import vt.utils.errors.error_specs.exceptions
from vt.utils.commons.commons.string import generate_random_string

from logician.constants import LGCN_MAIN_CMD_NAME, LGCN_INFO_FP_ENV_VAR
from pprint import pp


def main(*commands: str, ls: bool, env_list: bool, fmt: str | None = None):
    """
    Assumes that each command supports -h option.

    :param commands: commands to get the logger configurator details for.
    :param ls: Use long listing format
    :param env_list: show supported env vars.
    :param fmt: list in supplied formats. Can only be used when ``ls`` is True.
    :return:
    :raises VTCmdException: if error in running ``<<supplied-command>> --help`` for each command.
    """
    cmd_det_dict: dict[str, dict[str, dict[str, Any]]] = dict()
    env_fp = Path(
        tempfile.gettempdir(),
        f".0-LGCN-{'-'.join(commands)}-{generate_random_string()}.json",
    )
    os.environ[LGCN_INFO_FP_ENV_VAR] = str(env_fp)
    from logician._repo import get_repo

    get_repo().init()
    for command in commands:
        env_fp.write_text("")  # quick and dirty way to reinitialise the repo files.
        # This logic must somehow be handled into the repo provider itself.
        # TODO: If the env_fp.write("") statement is removed then, the file present in the /tmp dir formed by env_fp
        #  remains with the previous command's logger-configurator details. This is erroneous as then any command which
        #  does not use logger-configurators actually gets the configurator details which are already stored in the
        #  env_fp file from the previous command run.
        #  To get a feel of what this error entails, run these two commands:
        #  lgcn grep <a-command-that-uses-logician> # this will output grep: {}, i.e. grep has no logger-configurators
        #  lgcn <a-command-that-uses-logician> grep # this will output grep: <details-of-logger-configurators-of-the-second-program>,
        #  i.e. grep is incorrectly shown the logger configurator values of other programs as the env_fp file still
        #  stores those details from the previous run.
        #  FIX THIS!
        try:
            subprocess.run(
                [*shlex.split(command), "--help"], capture_output=True, check=True
            )
        except subprocess.CalledProcessError as e:
            raise vt.utils.errors.error_specs.exceptions.VTCmdException(
                f"Command failed: {e.cmd}",
                f"Stderr: {e.stderr}",
                f"Stdout: {e.stdout}",
                called_process_error=e,
                exit_code=e.returncode,
            ) from e
        get_repo().reload()
        cmd_det_dict[command] = get_repo().read_all()

    pp(cmd_det_dict)


def cli(args: list[str]) -> argparse.Namespace:
    """
    Examples:

    >>> cli(["cmd1"])
    Namespace(command=['cmd1'], ls=False, fmt=None, env_list=False)

    >>> cli(["cmd1", "cmd2"])
    Namespace(command=['cmd1', 'cmd2'], ls=False, fmt=None, env_list=False)

    >>> cli(["cmd1", "cmd2", "-l"])
    Namespace(command=['cmd1', 'cmd2'], ls=True, fmt=None, env_list=False)

    >>> cli(["cmd1", "cmd2", "-le"])
    Namespace(command=['cmd1', 'cmd2'], ls=True, fmt=None, env_list=True)

    >>> cli([])
    Traceback (most recent call last):
    ...
    SystemExit: 2

    >>> cli(['cmd1', '--fmt'])
    Traceback (most recent call last):
    ...
    SystemExit: 2

    :param args: arguments to the ``lgcn`` CLI.
    :return: Calculated ``argparse.Namespace`` from ``lgcn`` CLI.
    """

    parser = argparse.ArgumentParser(
        LGCN_MAIN_CMD_NAME,
        description=__doc__,
    )
    parser.add_argument(
        "command",
        help="get logger-configurator details of these commands. Assumes that all of these commands "
        "support the --help CLI option.",
        nargs="+",
    )
    lister_group = parser.add_argument_group(
        "listing", "options related to listing details about the logger-configurators"
    )
    lister_group.add_argument(
        "-l", "--list", action="store_true", help="Use long listing format.", dest="ls"
    )
    lister_group.add_argument(
        "--fmt",
        "--format",
        const="{name}\t{level}\t{vq-support}\t{env-support}",
        nargs="?",
        help="""Print formatted information about logger-configurators.
                              More headers, like, {lib}, {stream}, {no-of-handlers}, ...etc are available.
                              check documentation. Can only be used with -l option""",
        dest="fmt",
    )
    parser.add_argument(
        "-e",
        "--env-list",
        action="store_true",
        help="Get supported environment variables list.",
    )
    namespace = parser.parse_args(args)
    if namespace.fmt and not namespace.ls:
        parser.error("--format is only allowed with --list")
    return namespace


def main_cli(args: list[str] | None = None):
    args = args if args else sys.argv[1:]
    namespace = cli(args)
    main(
        *namespace.command,
        ls=namespace.ls,
        env_list=namespace.env_list,
        fmt=namespace.fmt,
    )


if __name__ == "__main__":
    main_cli()
