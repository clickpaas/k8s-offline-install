#!/bin/python
# _*_ coding: utf-8

import os

import sys
from common.utils import ColorPrompt, get_project_root_path, general_syscmd_execute
from config import work_temp_dir
from config import hosts, SupportFormatHostname
from common.cus_cmd import RemoteCommand, LocalCommand
from common.node import VirtualMachine
from common.error import Error


def validate_environment():
    def panic_if_necessary(ip, password):
        osv = VirtualMachine.get_os_version(ip, password)
        osv.get_data()
        assert osv.Success == osv.get_code(), "OsVersion validate failed: {}, code:{}".format(osv.get_msg(),
                                                                                              osv.get_code())

    ColorPrompt.stage_info("Begin to gather node information")
    ColorPrompt.stage_info("\t[0]OperationSystemVersionCheck")
    ret_os = {}
    ColorPrompt.stage_info("\t Validate Master")
    for i in hosts.get("master"):
        if len(i) == 0: continue
        panic_if_necessary(i.get("ip"), i.get("password"))
    ColorPrompt.stage_info("\t Validate Other Node")
    for i in hosts.get("nodes"):
        if len(i) == 0: continue
        panic_if_necessary(i.get("ip"), i.get("password"))


# environment checkout : checkout sshpass is installed or not
def bootstrap_sshpass():
    ret = Error.default_ok()
    if os.path.exists("/usr/bin/sshpass"):
        print(ColorPrompt.normal_msg("sshpass has been installed"))
        return

    sshpass_location = os.path.join(get_project_root_path(), "packages/sshpass")
    err = general_syscmd_execute("yum localinstall {}/* -y".format(sshpass_location))

    if err[0] != 0:
        print("Install local sshpass rpm failed ,make sure sshpass installed first \n Reason:{}".format(err[1]))
        sys.exit(-1)
    else:
        print(ColorPrompt.normal_msg("Install sshpass successfully"))


# # environment checkout: checkout system environment valued
def bootstrap_enviroment(host, password):
    print(ColorPrompt.info_prefix() + "\t{}\tCheck firewalld and selinux swap".format(ColorPrompt.title_msg(host)))
    print(ColorPrompt.info_prefix() + "\t{}\tBegin to stop firewalld".format(ColorPrompt.title_msg(host)))
    disableFirewall = RemoteCommand.security_command(host, password, "systemctl stop firewalld.service && "
                                                                     "systemctl disable firewalld.service")
    print(ColorPrompt.info_prefix() + "\t{}\tBegin to disable selinux".format(ColorPrompt.title_msg(host)))
    disableSelinux1 = RemoteCommand.security_command(host, password,
                                                     "sed -i.bak 's/SELINUX=enforcing/SELINUX=disabled/' "
                                                     "/etc/selinux/config && setenforce 0")
    print(ColorPrompt.info_prefix() + "\t{}\tBegin to stop swap".format(ColorPrompt.title_msg(host)))
    stop_swap = RemoteCommand.security_command(host, password, "swapoff -a")

    err = LocalCommand.scp(host, password, os.path.join(get_project_root_path(), "packages/configure/k8s.conf"),
                           "/etc/sysctl.d/k8s.conf")

    err = LocalCommand.scp(host, password, os.path.join(get_project_root_path(), "packages/configure/k8s_module.conf"),
                           "/etc/modules-load.d/k8s_module.conf")

    err = RemoteCommand.security_command(host, password, "sysctl --system")

    err = RemoteCommand.security_command(host, password, "echo 1 >  /proc/sys/net/ipv4/ip_forward")

    if SupportFormatHostname:
        host_name_ctl = RemoteCommand.security_command(host, password,
                                                       "hostnamectl set-hostname k8s-{}".format(host.replace(".", "-")))

    return


def load_images(host, password, role):
    print(ColorPrompt.stage_info + ("[+]\t{}\tDocker Loading Image".format(host)))
    remote_img_path = os.path.join(work_temp_dir, "images")
    images = [os.path.join(os.path.join(work_temp_dir, "images"), _) for _ in
              os.listdir(os.path.join(os.path.dirname(os.path.relpath(__file__)), "images"))]

    list(map(lambda _: RemoteCommand.security_command(host, password, "docker load -i {}".format(_)), images))


def scp_packages_to_nodes(host, password):
    print(ColorPrompt.stage_info("[!]\t{}\tSCP Docker Images TO  Node".format(host)))
    project_path = os.path.abspath(os.path.dirname(__file__))
    images_path = os.path.join(project_path, "images")
    remote_img_path = os.path.join(work_temp_dir, "images")
    mkdir_images_path = RemoteCommand.security_command(host, password, "mkdir {} -pv".format(remote_img_path))

    # images = [os.path.join(images_path,_) for _ in IMAGE_CONF.get("nodes")]
    list(map(lambda img: (host, password,
                          os.path.join(images_path, img),
                          os.path.join(remote_img_path, img)),
             os.listdir(images_path)))

    print(ColorPrompt.stage_info("[!]\t{}\tSCP KUBELET RPMS TO This Node".format(host)))
    rpms_path = os.path.join(project_path, "packages/k8s")
    remote_rpms_path = os.path.join(work_temp_dir, "packages/k8s")
    mkdir_rpms_path = RemoteCommand.security_command(host, password, "mkdir {} -pv".format(remote_rpms_path))

    list(map(lambda rpm: LocalCommand.scp(host, password,
                                          os.path.join(rpms_path, rpm),
                                          os.path.join(remote_rpms_path, rpm)),
             os.listdir(rpms_path)))

    print(ColorPrompt.stage_info("[!]\t{}\tSCP Docker RPMS TO This Node".format(host)))
    rpms_path = os.path.join(project_path, "packages/docker")
    remote_rpms_path = os.path.join(work_temp_dir, "packages/docker")
    mkdir_rpms_path = RemoteCommand.security_command(host, password, "mkdir {} -pv".format(remote_rpms_path))
    list(map(lambda rpm: LocalCommand.scp(host, password,
                                          os.path.join(rpms_path, rpm),
                                          os.path.join(remote_rpms_path, rpm)),
             os.listdir(rpms_path)))
