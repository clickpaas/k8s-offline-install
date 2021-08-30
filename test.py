#!/bin/python

from common.node import VirtualMachine
from common.network import get_networks
from common.utils import get_project_root_path
from pre_install import validate_environment

fake_hostname="10.77.13.208"
fake_hostname_tpl="k8s-{}"
fake_user = "root"
fake_password = "Abcd@123"


def test():
    get_project_root_path()



if __name__ == '__main__':
    test()