#!/usr/bin/env python3
# coding=utf-8

"""
Utility functions for logging related library.
"""

def command_or_file(command_name: str, file_name: str) -> str:
    """
    Useful in instances where a file may be either run as a library or a command. In such a case, mostly loggers must
    have appropriate names.

    Run as a library: A logger may be named as the file name (e.g. ``vt.utils.error.err_handler.err_funcs``)
    when it is run as a library or is used as a call from another file or command.

    Run as a command: When a file is run as a command then we'd need the logger to be named as the name of the command.
    Since files assume the name ``__main__`` when they're run directly as a command hence,the logger is then to be
    named as the command name.

    Examples:

    >>> command_or_file('a-cmd', 'vt.utils.error.err_handler.err_funcs')
    'vt.utils.error.err_handler.err_funcs'

    >>> command_or_file('a-cmd', '__main__')
    'a-cmd'

    :param command_name:
    :param file_name:
    :return: ``file_name`` if ``file_name`` is not ``__main__`` else ``command_name``.
    """
    return command_name if file_name == '__main__' else file_name
