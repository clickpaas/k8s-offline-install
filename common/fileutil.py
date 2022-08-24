#!/bin/python

import os


class FileUtil:
    def __init__(self): pass

    @staticmethod
    def list_rpm(path):
        return [os.path.basename(_) for _ in os.listdir(path) if _.endswith("rpm")]

    @staticmethod
    def list_tar(path):
        return [os.path.basename(_) for _ in os.listdir(path) if _.endswith("tar")]


if __name__ == '__main__':
    FileUtil.list_rpm("")
