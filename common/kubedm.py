#!/bin/python
import os
from .cus_cmd import RemoteCommand, LocalCommand
from common.utils import get_project_root_path

class KubernetesInstall:
    def __init__(self):pass

    @staticmethod
    def install_from_rpm(host, password):
        # mkdir tmp dirs
        err = RemoteCommand.security_command(host, password,"mkdir /tmp/k8s/rpm -pv")

        k8s_rpm = os.path.join(get_project_root_path(), "packages/k8s/rpm")
        list(map(lambda _: LocalCommand.scp(host, password, os.path.join(k8s_rpm, _), "/tmp/k8s/rpm"), os.listdir(k8s_rpm)))

        err = RemoteCommand.security_command(host, password, "yum localinstall /tmp/k8s/rpm/* -y")

        err = RemoteCommand.systemctl_enable(host, password, "kubelet")

        err = RemoteCommand.security_command(host, password, "rm -rf /tmp/k8s")

    @staticmethod
    def load_images(host, password):
        err = RemoteCommand.security_command(host, password, "mkdir /tmp/k8s/img/ -pv")

        k8s_img = os.path.join(get_project_root_path(), "packages/k8s/images/")
        # copy images
        list(map(lambda _: LocalCommand.scp(host, password, os.path.join(k8s_img,_), "/tmp/k8s/img"), os.listdir(k8s_img)))
        # load images
        list(map(lambda _: RemoteCommand.docker_load_image(host, password, os.path.join("/tmp/k8s/img", _)), os.listdir(k8s_img)))
        # delete tmp files
        err = RemoteCommand.security_command(host, password, "rm -rf /tmp/k8s/")

    @staticmethod
    def get_join_token(init):
        ret = {"node":None, "slave":None}
        _join, _discovery, _control_plan = "", "", ""
        for line in init.split("\n"):
            if "kubeadm join" in line and "discovery-token-ca-cert-hash" in line and "control-plane --certificate-ke" in line:
                ret['slave'] = line.strip('\\')
            elif "kubeadm join" in line and "discovery-token-ca-cert-hash" in line:
                ret['node'] = line.strip('\\')
            elif "kubeadm join" in line and "token" in line:
                _join = line.strip('\\')
            elif "--discovery-token-ca-cert-hash" in line:
                _discovery = line.strip('\\')
            elif "--control-plane --certificate-key" in line:
                _control_plan = line.strip('\\')

        node_join = " ".join([_join, _discovery])
        master_join = " ".join([_join, _discovery, _control_plan])

        if not ret.get("slave"):
            ret['slave'] = " ".join([_join, _discovery,_control_plan])
        if not ret.get("node"):
            ret['node'] = " ".join([_join, _discovery])
        return ret


