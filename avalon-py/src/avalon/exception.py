"""File that contains exception class used in the package avalon"""


class AvalonError(Exception):
    """Class AvalonError related to specific exception"""

    dict_log = {
        "critical": 50,
        "error": 40,
        "warning": 30,
        "info": 20,
        "debug": 10,
        "notset": 0
    }

    def __init__(self, msg, log_type="error"):
        print("[{}] {}".format(log_type.upper(), msg))
        Exception.__init__(self, msg)
