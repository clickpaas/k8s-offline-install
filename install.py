# coding:utf-8
import os
import sys
import re
import config
from common.utils import ColorPrompt, general_syscmd_execute, general_raw_input
from common import network
from common.cni_plugin import CniPlugin
from common.cus_cmd import RemoteCommand
from common.docker import DockerInstall
from pre_install import (
    bootstrap_sshpass,
    validate_environment,
    scp_packages_to_nodes,
    bootstrap_enviroment
)

from common.kubedm import KubernetesInstall

operationSystem = "centos" if os.path.exists("/etc/redhat-release") else "None"
pkg = "yum" if os == "centos" else "apt-get"
IP_COMPILE = re.compile("\d{,13}.\d{1,3}.\d{1,3}.\d{1,3}")

TEMP_SAVE_DIR = "/tmp/k8s/"


def main():
    ###############################################################################
    #                        Bootstrap  Env                                       #
    ###############################################################################
    print(ColorPrompt.stage_info("Bootstrap-->sshpass is installed or not"))
    bootstrap_sshpass()
    # check os version is validate, only support euler,centos(aliyun/tencent)
    # other os version like CentOS may be worker very well,but those may doesn't work sometimes
    # anyway you should  try it for all always to ensure it works
    print(ColorPrompt.stage_info("Validate OsVersion............"))
    # validate_environment()

    hosts = config.hosts

    all_nodes = hosts.get("master") + hosts.get("nodes") + hosts.get("slave")
    all_nodes = [_ for _ in all_nodes if _]

    print(ColorPrompt.stage_info("bootstrap base environment........."))
    list(map(lambda _: bootstrap_enviroment(_.get("ip"), _.get("password")), all_nodes))

    ###############################################################################
    #                        Select Network IFACE                                #
    ###############################################################################
    # network configure for controller plane
    print(ColorPrompt.stage_info("Gather Network Information......."))
    network_list = network.get_networks()
    if network_list.get_code() != network_list.Success:
        print(ColorPrompt.error_prefix() + "\tCan't Find Any Links In This Host")
        sys.exit(1)
    else:
        print(ColorPrompt.info_prefix() + "\tNetwork Information List In Current Host:")
        print(ColorPrompt.normal_msg("Current Network Information"))
        networks_info = network_list.get_data()
        assert isinstance(networks_info, dict), "except got dict from get_networks, but got {}".format(
            type(networks_info))
        _network_list = networks_info.items()
        count = 0
        for info in _network_list:
            print('Index:[' + ColorPrompt.ensure_show(count) + ']\tIface:[{:^32}]\tIp:[{:^12}]'.
                  format(ColorPrompt.ensure_show(info[0]), ColorPrompt.ensure_show(info[1])))
            count += 1

        _k8sapi_ip_or_index = general_raw_input(ColorPrompt.ensure_show(
            "Enter an network index [0- {}] or Enter an Ip address:".format(len(networks_info) - 1)))
        get_ip_address = IP_COMPILE.findall(_k8sapi_ip_or_index)
        if get_ip_address:
            api_server_addr = get_ip_address[0]
            print(ColorPrompt.ensure_show("You Choice {} for K8s Api server".format(get_ip_address[0])))
        else:

            assert int(_k8sapi_ip_or_index) < len(networks_info), "Illegal Index"
            api_server_addr = list(networks_info.values())[int(_k8sapi_ip_or_index)]
            print(ColorPrompt.ensure_show("You Choice {} for K8s Api server".format(api_server_addr)))

    # network configure for data plane
    print(ColorPrompt.info_prefix() + "\tConfig Data Interface")
    data_plane_interface = general_raw_input(
        ColorPrompt.ensure_show("plz choice network interface index for data traffic[0-{}]:".
                                format(len(networks_info) - 1)))
    assert int(data_plane_interface) < len(networks_info), "Illegal Index!"
    data_iface = list(networks_info.keys())[int(data_plane_interface)]

    ###############################################################################
    #                        Select & Config Cni                                  #
    ###############################################################################
    # select a cni plugin
    print("Index:[" + ColorPrompt.normal_msg("1") + "]\tPluginName:[{:^16}]".format(ColorPrompt.normal_msg("Flannel")))
    print("Index:[" + ColorPrompt.normal_msg("2") + "]\tPluginName:[{:^16}]".format(ColorPrompt.normal_msg("Calico")))
    network_plugin = int(general_raw_input(ColorPrompt.prompt("Enter you chose[1|2]: ")))

    # default cni config
    cni_name = "flannel"
    pod_network = "10.244.0.0/16"
    if network_plugin == 1:
        pod_network = "10.244.0.0/16"
        cni_name = "flannel"
    elif network_plugin == 2:
        pod_network = "192.168.0.0/16"
        cni_name = "calico"
    else:
        print("error network plugin")

    if not all_nodes:
        print(ColorPrompt.error_prefix() + "No Master and No Nodes, plz check config.py")

    ###############################################################################
    #                        Show Configure to User Confirm                       #
    ###############################################################################

    print(ColorPrompt.info_prefix() + "\t[{:^12}]\t[{:^16}]".format("ApiServer",
                                                                    ColorPrompt.normal_msg(api_server_addr)))
    print(ColorPrompt.info_prefix() + "\t[{:^12}]\t[{:^16}]".format("NetPlugin",
                                                                    ColorPrompt.normal_msg(cni_name)))
    for master in hosts.get("master"):
        if not master: continue
        host, passwd = master.get("ip"), master.get("password")
        print(ColorPrompt.info_prefix() + "\t[{:^12}]\t[HOST:{:^16}]\t[PASS:{:^16}]".format("Master",
                                                                                            ColorPrompt.normal_msg(
                                                                                                host),
                                                                                            ColorPrompt.normal_msg(
                                                                                                passwd)))
    for node in hosts.get("nodes"):
        if not node: continue
        host, passwd = node.get("ip"), node.get("password")
        print(ColorPrompt.info_prefix() + "\t[{:^12}]\t[HOST:{:^16}]\t[PASS:[{:^16}]".format("Nodes",
                                                                                             ColorPrompt.normal_msg(
                                                                                                 host),
                                                                                             ColorPrompt.normal_msg(
                                                                                                 passwd)))
    for node in hosts.get("slave"):
        if not node: continue
        host, passwd = node.get("ip"), node.get("password")
        print(ColorPrompt.info_prefix() + "\t[{:^12}]\t[HOST:{:^16}]\t[PASS:[{:^16}]".format("Slave",
                                                                                             ColorPrompt.normal_msg(
                                                                                                 host),
                                                                                             ColorPrompt.normal_msg(
                                                                                                 passwd)))
    print(ColorPrompt.info_prefix() + "\t[{:^12}]\t[{:^24}]".format("Data-Iface", ColorPrompt.normal_msg(data_iface)))
    confirm = general_raw_input(ColorPrompt.prompt("Above all information are correct?[Y/N]:"))
    if confirm.lower() != "y":
        sys.exit(0)

    ###############################################################################
    #                        Should kubeadm rest                                  #
    ###############################################################################
    # if kubeadm has been installed plz make sure reset it
    pre_installed_kubeadm = general_raw_input(ColorPrompt.prompt("Kubeadm has been installed in previous[Y|N]:"))
    if pre_installed_kubeadm.lower() == 'y':
        command = "kubeadm reset -f"
        list(map(lambda _: RemoteCommand.security_command(_.get("ip"), _.get("password"), command), all_nodes))

    ###############################################################################
    #                       Install Docker for All Node                           #
    ###############################################################################
    # install docker for all nodes
    print(ColorPrompt.stage_info("Install docker stage"))
    list(map(lambda _: DockerInstall.install_from_binary(_.get("ip"), _.get("password")), all_nodes))

    ###############################################################################
    #                       Install Kubeadm for All Node                          #
    ###############################################################################
    print(ColorPrompt.stage_info("Install kubeadm packages stage"))
    # install k8s rpm
    print(ColorPrompt.stage_info("begin install kubernetes rpm"))
    list(map(lambda _: KubernetesInstall.install_from_rpm(_.get("ip"), _.get("password")), all_nodes))
    # load images
    print(ColorPrompt.stage_info("begin load k8s some docker images to host"))
    list(map(lambda _: KubernetesInstall.load_images(_.get("ip"), _.get("password")), all_nodes))

    # # begin init kubeadm
    print(ColorPrompt.stage_info("Kubeadm init stage"))
    def sync_host_record(host, password):
        RemoteCommand.security_command(host,password, 'echo "{}  {}"'.format(api_server_addr, config.ApiServerDomain))
    if config.ApiServerDomain:
        list(map(lambda _: sync_host_record(_.get("ip"), _.get("password")), all_nodes))
        api_server_addr = config.ApiServerDomain

    print('./kubeadm init  --kubernetes-version={} --pod-network-cidr={}  --control-plane-endpoint {} --upload-certs'. \
          format(config.KubernetesVersion, pod_network, api_server_addr))
    init = general_syscmd_execute(
        './kubeadm init  --kubernetes-version={} --pod-network-cidr={}  --control-plane-endpoint {} '
        '--upload-certs'.format(config.KubernetesVersion, pod_network, api_server_addr))
    #
    if init[0] != 0:
        print(ColorPrompt.info_prefix() + "\t./kubeadm init Failed,Reason is:{}".format(ColorPrompt.err_msg(init[1])))
        sys.exit(1)
    k8s_join_cmd = KubernetesInstall.get_join_token(init[1])
    #
    general_syscmd_execute("mkdir -pv ~/.kube && cp -f /etc/kubernetes/admin.conf /root/.kube/config")

    print(ColorPrompt.stage_info("load cni images {} stage".format(cni_name)))
    cni_plugin = CniPlugin(cni_name)
    list(map(lambda _: cni_plugin.load_cni_images(_.get("ip"), _.get("password")),[_ for _ in hosts.get("nodes") + hosts.get("slave") if _]))

    print(ColorPrompt.stage_info("Kube Master Join stage"))
    print(ColorPrompt.info_prefix() + "Master Join cmd is : {}".format(k8s_join_cmd.get("slave")))
    for sighost in hosts.get("slave"):
        if not sighost: continue
        host, password = sighost.split("/")
        result = RemoteCommand.security_command(host, password, k8s_join_cmd.get("slave"))

    print(ColorPrompt.stage_info("Kube Node Join stage"))
    print(ColorPrompt.info_prefix() + "Node Join cmd is : {}".format(k8s_join_cmd.get("node")))
    list(map(lambda _: RemoteCommand.security_command(_.get("ip"), _.get("password"), k8s_join_cmd.get("node")),[_ for _ in hosts.get("nodes") if _]))

    cni_plugin.apply_yaml(data_plane_interface)


if __name__ == '__main__':
    main()
