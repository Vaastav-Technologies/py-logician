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

from vt.utils.commons.commons.string import generate_random_string

from logician.constants import LGCN_MAIN_CMD_NAME, LGCN_INFO_FP_ENV_VAR
from pprint import pp


def main(*commands: str, ls: bool, env_list: bool, fmt: str | None = None):
    """
    Assumes that each command supports -h option.

    :param commands:
    :param ls:
    :param env_list:
    :param fmt:
    :return:
    """
    cmd_det_dict: dict[str, dict[str, dict[str, Any]]] = dict()
    env_fp = Path(tempfile.gettempdir(), f".0-LGCN-{'-'.join(commands)}-{generate_random_string()}.json")
    os.environ[LGCN_INFO_FP_ENV_VAR] = str(env_fp)
    from logician._repo import get_repo
    get_repo().init()
    for command in commands:
        command = shlex.split(command)[0]
        subprocess.run([command, "--help"], capture_output=True, check=True)
        get_repo().reload()
        cmd_det_dict[command] = get_repo().read_all()

    pp(cmd_det_dict)


def cli(args: list[str]) -> argparse.Namespace:
    """

    :param args:
    :return:
    """

    parser = argparse.ArgumentParser(LGCN_MAIN_CMD_NAME, description=__doc__, )
    parser.add_argument('command',
                        help='get logger-configurator details of these commands. Assumes that all of these commands '
                             'support the --help CLI option.', nargs='+')
    lister_group = parser.add_argument_group("listing", "options related to listing details about "
                                                        "the logger-configurators")
    lister_group.add_argument("-l", "--list", action="store_true", help="Use long listing format.",
                              dest="ls")
    lister_group.add_argument("--format", const="{name}\t{level}\t{vq-support}\t{env-support}", nargs='?',
                              help="""Print formatted information about logger-configurators.
                              More headers, like, {lib}, {stream}, {no-of-handlers}, ...etc are available.
                              check documentation.""",
                              dest="fmt")
    parser.add_argument("-e", "--env-list", action="store_true", help="Get supported environment "
                                                                      "variables list.")
    namespace = parser.parse_args(args)
    if namespace.fmt and not namespace.ls:
        parser.error("--format is only allowed with --list")
    return namespace


def main_cli(args: list[str] | None = None):
    args = args if args else sys.argv[1:]
    namespace = cli(args)
    main(*namespace.command, ls=namespace.ls, env_list=namespace.env_list, fmt=namespace.fmt)


if __name__ == '__main__':
    main_cli()
