#!/bin/python
# _*_coding: utf-8

import node
from config import work_temp_dir
from cus_cmd import RemoteCommand, LocalCommand
from commands import getoutput


def add_nvidia_support(host, password):
    project_path = node.path.dirname(node.path.dirname(node.path.abspath(__file__)))

    nvidia_img_src = node.path.join(project_path, "gpu", "images")
    remote_nvidia_path = node.path.join(work_temp_dir, "gpu", "images")
    _mkdir_remote_nvidia_path = RemoteCommand.security_command(host, password, "mkdir {} -pv".format(remote_nvidia_path))

    # scp
    _scp = map(lambda img: LocalCommand.scp(host, password,
                               node.path.join(nvidia_img_src, img),
                               node.path.join(remote_nvidia_path, img)),
               node.listdir(nvidia_img_src))

    # load
    _load = map(lambda img: RemoteCommand.security_command(host, password, "docker load -i {}/{}".format(remote_nvidia_path, img)),
                node.listdir(nvidia_img_src))

    # apply
    _ = getoutput("kubectl apply -f {}/yaml/".format(node.path.join(project_path, "gpu", "yaml")))

