#!/bin/python
# _*_coding: utf-8

from common._termcolor import colored
import os
import subprocess
import platform


def is_python2():
    python_version = platform.python_version_tuple()
    if python_version[0] == "2" and int(python_version[1]) >= 7:
        return True
    elif python_version[1] == "3":
        return False

# general_xxx method is used for support multiple python(for python2 and python3)
def general_raw_input(prompt_msg):
    if is_python2():
        return raw_input(prompt_msg)
    return input(prompt_msg)


def general_syscmd_execute(cmd):
    """
    Args:
        cmd:

    Returns: (code, ret)

    """
    if is_python2():
        from commands import getstatusoutput
        return getstatusoutput(cmd)
    return subprocess.getstatusoutput(cmd)



class ColorPrompt:
    def __init__(self):
        pass

    @staticmethod
    def info_prefix():
        return "[" + colored("Info", "green") + "]"

    @staticmethod
    def warn_prefix():
        return "[" + colored("Warn", "yellow") + "]"

    @staticmethod
    def error_prefix():
        return "[" + colored("Error", "red") + "]"

    @staticmethod
    def title_msg(msg):
        return colored(msg, 'blue', attrs=['reverse'])

    @staticmethod
    def normal_msg(msg):
        return colored(msg, on_color="on_blue")

    @staticmethod
    def err_msg(msg):
        return colored(msg, on_color='on_red')

    @staticmethod
    def prompt(msg):
        return colored(msg, "blue")

    @staticmethod
    def stage_info(msg):
        return colored(msg, 'grey', attrs=['bold'])

    @staticmethod
    def ensure_show(msg):
        return colored(msg, "magenta")


def get_project_root_path():
    return os.path.abspath(os.curdir)


if __name__ == '__main__':
    get_project_root_path()
