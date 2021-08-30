#!/bin/python

from config import work_temp_dir
from common import utils
import config

def clearn_all_package():
    cmd = "rm -rf {}".format(work_temp_dir)
    hosts = config.hosts
    for sighost in hosts.get("nodes") + hosts.get("master") + hosts.get("slave"):
        if not sighost: continue
        host, password = sighost.split("/")
        utils.security_command(host, password, cmd)
