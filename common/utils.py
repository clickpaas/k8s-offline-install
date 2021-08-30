#!/bin/python
# _*_coding: utf-8

from common._termcolor import colored
import os


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

