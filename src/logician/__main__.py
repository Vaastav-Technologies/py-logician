#!/usr/bin/env python3
# coding=utf-8

"""
Extract and showcase details about a program's logger configurators.
"""

import sys
import argparse
import subprocess

from logician.constants import LGCN_MAIN_CMD_NAME


def main_cli(args: list[str] | None = None):
    args = args if args else sys.argv[1:]
    parser = argparse.ArgumentParser(LGCN_MAIN_CMD_NAME, description=__doc__,)
    parser.add_argument('command',
                        help='get logger-configurator details of these commands', nargs='+')
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("--format", const="{name}\t{level}\t{vq-support}\t{env-support}", nargs='?')
    parser.add_argument("-e", "--env-list", action="store_true")
    print(parser.parse_args(args))


if __name__ == '__main__':
    main_cli()
