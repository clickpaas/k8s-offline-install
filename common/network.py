#!/bin/python

import re
from common.error import Error
from .utils import general_syscmd_execute


def get_networks():
    def get_ip_from_iface(iface):
        ip_reg = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}/\d{1,3}")
        ip_str = general_syscmd_execute("ip addr show {}|grep inet|grep -v inet6".format(iface))
        if ip_str[0] != 0:
            return {}
        _ = ip_reg.findall(ip_str[1])
        ip = None if not _ else None if not _[0].split('/')[0] else _[0].split('/')[0]
        return {iface: ip} if ip else {}

    ret = {}
    all_interfaces = general_syscmd_execute("ip link show|grep UP|awk -F': ' '{print $2}'")
    if all_interfaces[0] != 0:
        return Error.new(Error.NotFound, "not found interface", "")
    all_if = [_ for _ in all_interfaces[1].split("\n")]
    list(map(lambda _: ret.update(get_ip_from_iface(_)), all_if))
    return Error.new(Error.Success, "", ret)
