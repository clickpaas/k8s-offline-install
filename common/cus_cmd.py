#!/bin/python
from commands import getstatusoutput
from utils import ColorPrompt
from common.error import Error


# RemoteCommand is used to execute bash command in remote host
class RemoteCommand:
    def __init__(self):
        pass

    # security_command used to execute common bash command in remote host, this method is more generic
    @staticmethod
    def security_command(host, password, command):
        ret = Error.default_ok()
        flag = getstatusoutput('sshpass -p {} ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -q root@{} "{}"'.
                               format(password, host, command))
        if flag[0] != 0:
            ret.set_code(ret.Failed)
            ret.set_msg(flag[1])
        else:
            ret.set_code(ret.Success)
            ret.set_msg("")
            ret.set_data(flag[1])
        return ret

    # yum_local_install used to execute yum local install command in remote host, is only for yum
    @staticmethod
    def yum_local_install(host, password, target):
        cmd = "yum localinstall {} -y".format(target)
        return RemoteCommand.security_command(host, password, cmd)

    @staticmethod
    def swap_off(host, password):
        cmd = "sed -i 's/.*swap.*/#&/' /etc/fstab && swapoff -a"
        return RemoteCommand.security_command(host, password, cmd)

    @staticmethod
    def firewalld_stop(host, password):
        cmd = "systemctl disable firewalld && systemctl stop firewalld"
        return RemoteCommand.security_command(host, password, cmd)

    @staticmethod
    def systemctl_enable(host, password, svc):
        cmd = "systemctl enable {}".format(svc)
        return RemoteCommand.security_command(host, password, cmd)

    @staticmethod
    def systemctl_start(host, password, service):
        cmd = "systemctl start {}".format(service)
        return RemoteCommand.security_command(host, password, cmd)

    @staticmethod
    def docker_load_image(host, password, image):
        cmd = "docker load -i {}".format(image)
        return RemoteCommand.security_command(host, password, cmd)


# LocalCommand is used to execute bash command in local host machine
class LocalCommand:
    def __init__(self):
        pass

    # scp command is used to copy some file in local host machined to remote hosts
    @staticmethod
    def scp(host, password, src, dest):
        flag = getstatusoutput(
            'sshpass -p {} scp  -o StrictHostKeyChecking=no {} root@{}:{}'.format(password, src, host, dest))
        if flag[0] != 0:
            print ColorPrompt.error_prefix() + "\t{}\tscp {} failed: Reason: {}".format(ColorPrompt.title_msg(host), dest,
                                                                                        ColorPrompt.err_msg(flag[1]))
            msg = "scp {} to {}:{} failed".format(src, host, dest)
            return Error.new(Error.Failed, msg, "")
        print ColorPrompt.info_prefix() + "\t{}\tscp {} successfully".format(ColorPrompt.title_msg(host), dest)
        return Error.new(Error.Success, "", "")
