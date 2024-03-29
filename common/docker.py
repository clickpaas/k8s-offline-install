#!/bin/python
# _*_ coding:utf-8

import os
from config import work_temp_dir
from common.cus_cmd import RemoteCommand, LocalCommand
from common.utils import ColorPrompt, general_raw_input, get_project_root_path


class DockerInstall:
    def __init__(self):
        pass

    @staticmethod
    def install_from_binary(host, password):
        # scp docker binary file to remote host
        docker_package = os.path.join(get_project_root_path(), "packages/containerd")
        allfiles = [os.path.join(docker_package, _) for _ in os.listdir(docker_package)]
        list(map(lambda _: LocalCommand.scp(host, password, _, os.path.join("/usr/local/bin/", os.path.basename(_))), allfiles))
        list(map(lambda _: RemoteCommand.security_command(host, password, "chmod +x /usr/local/bin/{}".format(os.path.basename(_))), allfiles))
        #  scp service file to remote host
        err = RemoteCommand.security_command(host, password, "mkdir /etc/containerd/ -pv")
        err = LocalCommand.scp(host, password,
                               os.path.join(get_project_root_path(), "packages/configure/containerd.service"),
                               "/etc/systemd/system/containerd.service")
        err = LocalCommand.scp(host, password, os.path.join(get_project_root_path(), "packages/configure/containerd.toml"), "/etc/containerd/config.toml")
        err = RemoteCommand.systemctl_enable(host, password, "containerd")
        err = RemoteCommand.systemctl_start(host, password, "containerd")

    @staticmethod
    def install_from_rpm(host, password):
        ret = {"code": 0, "msg": "", "data": ""}
        project_path = get_project_root_path()
        docker_rpms = os.path.join(project_path, "packages/docker")
        remote_docker_rpm_path = os.path.join(work_temp_dir, "packages/docker")
        installdocker = RemoteCommand.security_command(host, password,
                                                       "yum localinstall {}/*.rpm -y".format(remote_docker_rpm_path))
        assert isinstance(installdocker, dict), "expect got dict, but got {}".format(type(installdocker))
        if installdocker.get("code") or "Complete" not in installdocker.get("data"):
            ret['code'] = 500
            ret['msg'] = installdocker.get("msg")
            ret['data'] = installdocker.get("data")
        return ret

    @staticmethod
    def install_from_repo(host, password):
        add_plugin = RemoteCommand.security_command(host, password,
                                                    "yum install device-mapper-persistent-data yum-utils lvm2 -y")

        if add_plugin[0]:
            print(add_plugin + "please conform plugin has been installed")
        else:
            return add_plugin
        add_repo = RemoteCommand.security_command(host, password,
                                                  "yum-config-manager --add-repo "
                                                  "https://download.docker.com/linux/centos/docker-ce.repo")
        print(add_repo[0])
        if add_repo:
            return add_repo
        install_docker = RemoteCommand.security_command(host, password, "yum install docker-ce -y")
        print(install_docker)
        if install_docker[0]:
            return install_docker
        else:
            return 0

    @staticmethod
    def validate(host, password):
        _get_docker_version = RemoteCommand.security_command(host, password,
                                                             "yum list installed|grep docker-ce|grep -v cli")

        dockerversion = "Not installed" if _get_docker_version.get("code") else _get_docker_version.get("data").split()[
            1]

        reinstall = general_raw_input("\t{}\t".format(host) + ColorPrompt.prompt(
            "docker current version is:" + "{}".format(ColorPrompt.err_msg(dockerversion))) + ColorPrompt.prompt(
            "Install/Reinstall? [Y/N]"))
        if reinstall.lower() != 'y':
            print(ColorPrompt.warn_prefix() + "{}\tSkip Install Docker".format(host))
            return
        removeOldVersionIfExisted = RemoteCommand.security_command(host, password, "yum remove -y docker*")
        if removeOldVersionIfExisted.get("code"):
            return removeOldVersionIfExisted

        # if install_docker_online(host,password):
        #     print ERROR + "\t{}\tInstall docker online Failed and Ready Install offline".format(host)
        # else:
        #     print INFO + "\t{}\tInstall docker online Successful".format(host)
        #     return 0
        _install_docker_offline_result = DockerInstall.install_from_rpm(host, password)
        if _install_docker_offline_result.get("code"):
            print(ColorPrompt.error_prefix() + "\t{}\tInstall docker offline Failed".format(host))
            assert False, "Install docker failed: for {} \t {}". \
                format(_install_docker_offline_result.get("msg"), _install_docker_offline_result.get("data"))
        print(ColorPrompt.info_prefix() + "\t{}\tInstall docker offline Successful".format(host))

        enableDocker = RemoteCommand.security_command(host, password,
                                                      "systemctl enable docker && systemctl restart docker")

        return 0

    @staticmethod
    def nvidia_docker_config(host, password):
        # if daemon is existed and bckit
        _bak_old_daemon = "mv /etc/docker/daemon.json /etc/docker/daemon.bak"
        _ = RemoteCommand.security_command(host, password, _bak_old_daemon)
        # install nvidia-docker
        project_path = get_project_root_path()
        nvidia_src = os.path.join(project_path, "packages", "nvidia_docker")
        remote_nvidia = os.path.join(work_temp_dir, "packages", "nvidia_docker")
        # mkdir remote_nvidia path
        _mkdir_remote_nvidia = RemoteCommand.security_command(host, password, "mkdir {} -pv".format(remote_nvidia))
        # kaobei rpm
        list(map(lambda rpm: LocalCommand.scp(host, password, os.path.join(nvidia_src, rpm),
                                              os.path.join(remote_nvidia, rpm)),
                 [_ for _ in os.listdir(nvidia_src) if _ != "daemon.json"]))

        # install
        _ = RemoteCommand.security_command(host, password, "yum localinstall {}/*.packages".format(remote_nvidia))

        # scp daemon to
        _ = LocalCommand.scp(host, password, os.path.join(nvidia_src, "daemon.json"), "/etc/docker/daemon.json")

        # reload docker
        _ = RemoteCommand.security_command(host, password, "systemctl restart docker")
