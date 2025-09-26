from vt.utils.errors.error_specs.exceptions import VTException, VTExitingException, VTCmdException, VTCmdNotFoundError


class LogicianException(VTException):
    """
    Exception particular to ``logician``.
    """
    pass


class LogicianExitingException(LogicianException, VTExitingException):
    """
    A ``logician`` exception that allows exiting with an ``error_code``.
    """
    pass


class LogicianCmdException(LogicianExitingException, VTCmdException):
    """
    A ``logician`` exception that can denote exceptional scenario from a command run.
    """
    pass


class LogicianCmdNotFoundError(LogicianExitingException, VTCmdNotFoundError):
    """
    A ``logician`` exception that specifies a command not found.
    """
    pass
