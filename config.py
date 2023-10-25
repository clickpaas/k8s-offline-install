# coding:utf-8
# 如果禁用scp，只需要填写IP地址就可以，用户名和密码随意填写下
# 如果允许scp并且客户提供用户名和密码，按照固定格式填写
hosts = {
    "master": [
        {"ip": "172.17.0.2", "user": "root", "password": "xxxxxxx"},
    ],  # master节点的ip地址/密码
    "slave": [
        {"ip": ""}
    ],  # slave node,
    "nodes": [
        {"ip": "", "user":"root", "password": "xxxx"},
    ],  # work节点的ip地址/密码 列表
}

# if gpus node existed ,noted here
gpus = []

work_temp_dir = "/tmp/k8s"

# "10.23.6.50/root"

# version of kubernetes should be installed
KubernetesVersion = "1.27.2"

# should use ssh
# True, it will auto install docker && kubernetes on all host in config.hosts
# False, it will only install docker && kubernetes on local machines
SupportScpTransform = True

# should change hostname ?
# if set True , it will change hostname to k8s-ip, for some machine's hostname is localhost.local_domain, it should be set True
# if set False ,it will do nothing about hostname
SupportFormatHostname = False

# should support ha
# None => will use the ipaddress of current machine as the apiserver address
# some_domain
ApiServerDomain = "kubernetes.default"
