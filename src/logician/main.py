#!/usr/bin/env python3
# coding=utf-8

"""
Extract and showcase details about a program's logger configurators.
"""
from logician.errors import LogicianExitingException, LogicianCmdException, LogicianCmdNotFoundError, LogicianException

# TODO: add extensive examples in the README. Better yet, create a whole separate file/section for examples.

examples = """
Examples:

Just see the logger names of a command that uses logician:

    # use `lgcn command [command...]` syntax    
    $ lgcn prog-using-logician another-prog-using-lgcn prog-using-lgcn-but-no-loggers prog-not-using-lgcn
    prog-using-logician: ['prog', 'prog.child', 'sibling'] # list of logger names
    ano-prog-using-lgcn: ['r', 'r.c', 's', 's.c'] # list of logger names
    prog-using-lgcn-but-no-loggers: [] # no logger names visible
    # prog-not-using-lgcn is not visible.
    
Use the long listing format:

    # using `lgcn -l command [command...]` syntax
    # uses default `{cmd}\t{name}\t{level}\t{vq-support}\t{env-support}` format
    $ lgcn -l prog-1 prog-2 prog-3
    command             logger              level               vq-support          env-support         
    ----------------------------------------------------------------------------------------------------
    prog-1              ro                  Level 14            False                ['IN_ENV', 'IN.ENV']
    prog-1              ro.or               Level 14            False               False
    prog-1              r                   Level 32            True                ['ENV']
    prog-1              r.c                 Level 32            True                ['ENV.C', 'ENV_C', 'ENV']
    prog-1              c.r                 Level 12            False               False
    prog-2              .ano                WARNING             False               {}
    
    # prog-1 and prog-2 use logician, prog-3 doesn't.
    # vq-support denotes whether the env-vars can take 'v', 'vv', 'vvv' for verbosity levels and 
    # 'q', 'qq', 'qqq' for quietness level settings.
    
List all the log env-vars supported by programs:

    # using `lgcn -e command [command...]` syntax
    $ lgcn -e prog-1 prog-2 prog-3
    prog-1: ['IN_ENV', 'IN.ENV', 'ENV', 'ENV.C', 'ENV_C', 'ENV']
    prog-2: []
    
    # prog-1 uses logician and exposes ['IN_ENV', 'IN.ENV', 'ENV', 'ENV.C', 'ENV_C', 'ENV'] env-vars
    # prog-2 uses logician but does not export any env-vars.
    # prog-3 does not use logician
    
Use long listing format with env-vars:

    # using `lgcn -l -e command [command...]` syntax
    # uses default `{cmd}\t{name}\t{level}\t{vq-support}\t{env-support}` format
    $ lgcn -le prog-1 prog-2 prog-3
    command             logger              level               vq-support          env-support         
    ----------------------------------------------------------------------------------------------------
    prog-1              ro                  Level 14            False                ['IN_ENV', 'IN.ENV']
    prog-1              ro.or               Level 14            False               []
    prog-1              r                   Level 32            True                ['ENV']
    prog-1              r.c                 Level 32            True                ['ENV.C', 'ENV_C', 'ENV']
    prog-1              c.r                 Level 12            False               []
    prog-2              .ano                WARNING             False               []

    # prog-1 uses logician and exposes ['IN_ENV', 'IN.ENV', 'ENV', 'ENV.C', 'ENV_C', 'ENV'] env-vars
    # prog-2 uses logician but does not export any env-vars.
    # prog-3 does not use logician
    
"""

import os
import shlex
import sys
import argparse
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from vt.utils.commons.commons.string import generate_random_string

from vt.utils.errors.error_specs import ERR_INVALID_USAGE, ERR_CMD_NOT_FOUND

from logician.constants import LGCN_MAIN_CMD_NAME, LGCN_INFO_FP_ENV_VAR

CONST_FMT = "{cmd}\t{name}\t{level}\t{vq-support}\t{env-support}"


def main(*commands: str) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Assumes that each command supports -h option.

    :param commands: commands to get the logger configurator details for.
    :return: a dictionary of command and their individual logger-configurator properties.
    :raises VTCmdException: if error in running ``<<supplied-command>> --help`` for each command.
    """
    cmd_det_dict: dict[str, dict[str, dict[str, Any]]] = dict() # pragma: no cover
    env_fp: Path = Path(
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
        except FileNotFoundError as f:
            raise LogicianCmdNotFoundError(command=shlex.split(command), file_not_found_error=f,
                                           exit_code=ERR_CMD_NOT_FOUND) from f
        except subprocess.CalledProcessError as e:
            raise LogicianCmdException(
                f"Command failed: {e.cmd}",
                f"Stderr: {e.stderr}",
                f"Stdout: {e.stdout}",
                called_process_error=e,
                exit_code=e.returncode,
            ) from e
        get_repo().reload()
        cmd_det_dict[command] = get_repo().read_all()
    return cmd_det_dict


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
        add_help=False,
    )
    parser.add_argument(
        "command",
        help="get logger-configurator details of these commands. Assumes that all of these commands "
             "support the --help CLI option.",
        nargs="+",
    )
    # Helpers group
    helper_group = parser.add_argument_group("helps", "Get help regarding logician")
    helper_group.add_argument("-h", help="Show compact help and exit.", action="help")
    helper_group.add_argument("--help", help="Show extended help and exit.", action="help")
    lister_group = parser.add_argument_group(
        "listing", "options related to listing details about the logger-configurators"
    )
    lister_group.add_argument(
        "-l", "--list", action="store_true", help="Use long listing format.", dest="ls"
    )
    lister_group.add_argument(
        "--fmt",
        "--format",
        const=CONST_FMT,
        nargs="?",
        help="""Can only be used with -l option. 
        Print formatted information about logger-configurators. 
        More headers, like, {lib}, {stream}, {no-of-handlers}, ...etc are available. Check documentation.""",
        dest="fmt",
    )
    parser.add_argument(
        "-e",
        "--env-list",
        action="store_true",
        help="Get supported environment variables list.",
    )

    if "--help" in args:
        print(parser.format_help()+examples)
        sys.exit()

    namespace: argparse.Namespace = parser.parse_args(args)
    if namespace.fmt and not namespace.ls:
        parser.error("--format is only allowed with --list")
    return namespace


def main_view(info_dict: dict[str, dict[str, dict[str, Any]]], ls: bool, env_list: bool, fmt: str | None = None):
    """
    View that will print info about ``info_dict`` on ``stdout`` according to the required formats.

    Examples:

    >>> main_view(dict(), False, True, "{name}")
    Traceback (most recent call last):
    ...
    logician.errors.LogicianExitingException: ValueError: fmt cannot be used when ls is Falsy.

    >>> main_view(dict(), None, # type: ignore[arg-type]
    ...             True, "{name}")
    Traceback (most recent call last):
    ...
    logician.errors.LogicianExitingException: ValueError: fmt cannot be used when ls is Falsy.

    :param info_dict: mappings of commands and their individual logger configurator details.
    :param ls: Use long listing format
    :param env_list: show supported env vars.
    :param fmt: list in supplied formats. Can only be used when ``ls`` is True.
    """
    if fmt is not None and not ls:
        errmsg = "fmt cannot be used when ls is Falsy."
        raise LogicianExitingException(errmsg, exit_code=ERR_INVALID_USAGE) from ValueError(errmsg)

    el_det = defaultdict(list)  # env list details. cmd -> env-list mapping
    ls_det = defaultdict(dict)  # ls default details. cmd -> {name, level, vq_support, env_support}

    # Prepare env-vars
    for cmd in info_dict:
        for lgr in info_dict[cmd]:
            # Run for all the registered loggers.
            # makes sure that programs not using logician do not get registered here.
            if "env_list" in info_dict[cmd][lgr]:
                el_det[cmd].extend(info_dict[cmd][lgr]["env_list"])
            else:
                if not el_det[cmd]:
                    el_det[cmd] = []

    # Prepare list in the predetermined fmt
    for cmd in info_dict:
        for lgr in info_dict[cmd]:
            ls_det[cmd][lgr] = defaultdict(dict)
            if "vq" in info_dict[cmd][lgr]:
                ls_det[cmd][lgr]["vq_support"] = True
            else:
                ls_det[cmd][lgr]["vq_support"] = False

            if cmd in el_det:
                if "env_list" in info_dict[cmd][lgr]:
                    if env_list:
                        ls_det[cmd][lgr]["env_support"] = info_dict[cmd][lgr]["env_list"]
                    else:
                        ls_det[cmd][lgr]["env_support"] = True
                else:
                    if env_list:
                        ls_det[cmd][lgr]["env_support"] = []
                    else:
                        ls_det[cmd][lgr]["env_support"] = False
            ls_det[cmd][lgr]["level"] = info_dict[cmd][lgr]["level"]

    if ls:
        # Only print list in the predetermined fmt
        frmt = "{:<20}" * 5  # 5 columns
        print(frmt.format("command", "logger", "level", "vq-support", "env-support"))
        print("-"*20*5)
        for cmd, lgr in ls_det.items():
            [print(frmt.format(cmd, c, l["level"], str(l["vq_support"]), str(l["env_support"])))
             for c, l in lgr.items()]
        return

    if env_list:
        # Only print env-list per command
        [print(f"{c}: {l}") for c, l in el_det.items()]
        return

    # Simply print logger names per command
    ln_det = defaultdict(list)  # logger names per command
    for cmd in info_dict:
        for lgr in info_dict[cmd]:
            ln_det[cmd].append(lgr)
    [print(f"{c}: {l}") for c, l in ln_det.items()]


def main_cli(args: list[str] | None = None):
    """
    Main CLI, this runs:

    - Just the CLI to get namespace.
    - Main logic to get a mapping of command and its individual logger-configurators.
    - Print the command -> logger-configurator mappings according to user supplied options.

    :param args: CLI args to ``lgcn``.
    """
    try:
        args: list[str] = args if args else sys.argv[1:]
        namespace: argparse.Namespace = cli(args)
        info_dict: dict[str, dict[str, dict[str, Any]]] = main(*namespace.command, )
        main_view(info_dict, ls=namespace.ls, env_list=namespace.env_list, fmt=namespace.fmt, )
    except LogicianExitingException as le:
        print(le, file=sys.stderr)
        sys.exit(le.exit_code)
    except LogicianException as l:
        print(l, file=sys.stderr)


if __name__ == "__main__":
    main_cli()
