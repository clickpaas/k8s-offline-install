#!/bin/python
# _*_coding: utf-8

from os import path, listdir
from config import work_temp_dir
from cus_cmd import RemoteCommand, LocalCommand
from utils import general_syscmd_execute, get_project_root_path


def add_nvidia_support(host, password):
    project_path = get_project_root_path()

    nvidia_img_src = path.join(project_path, "gpu", "images")
    remote_nvidia_path = path.join(work_temp_dir, "gpu", "images")
    _mkdir_remote_nvidia_path = RemoteCommand.security_command(host, password,
                                                               "mkdir {} -pv".format(remote_nvidia_path))

    # scp
    _scp = list(map(lambda img: LocalCommand.scp(host, password, path.join(nvidia_img_src, img),
                                                 path.join(remote_nvidia_path, img)), listdir(nvidia_img_src)))

    # load
    _load = list(map(lambda img: RemoteCommand.security_command(host, password,
                                                                "docker load -i {}/{}".format(remote_nvidia_path, img)),
                     listdir(nvidia_img_src)))

    # apply
    _ = general_syscmd_execute("kubectl apply -f {}/yaml/".format(path.join(project_path, "gpu", "yaml")))
