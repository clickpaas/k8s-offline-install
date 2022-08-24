#!/bin/python

from common.cus_cmd import RemoteCommand
from common.error import Error

_Release_File = "/etc/redhat-release"

OS_Version_Mapping = {
    "Huawei-Eula": "EulerOS release 2.0 (SP2)",
    "Centos": "CentOS Linux release",
}
UnSupportOSVersion = "UnSupportOSVersion"


class VirtualMachine:
    def __init__(self):
        pass

    @staticmethod
    def get_hostname(host, password):
        pass

    @staticmethod
    def set_hostname(host, password, hostname):
        pass

    # get_os_version get operation system version from /etc/redhat-release file
    # return os version if matched OS_Version_Mapping, or return UnSupportOSVersion with type string
    @staticmethod
    def get_os_version(host, password):
        remote_read = RemoteCommand.security_command(host, password, "cat {}".format(_Release_File))
        if remote_read.get_code() != remote_read.Success:
            return remote_read

        for (k, v) in OS_Version_Mapping.items():
            if v in remote_read.get_data():
                return Error.default_ok()
            # if v == remote_read.get_data():
            #     return Error.default_ok()
            #
        return remote_read.wrap_error(Error.new(Error.Failed, UnSupportOSVersion))


if __name__ == '__main__':
    pass
