# coding:utf-8
hosts = {
    "master": [
        {"ip": "10.77.13.208", "user": "root", "password": "xxxxxxx"},
    ],		# master节点的ip地址/密码
    "slave": [
        {}
    ],       # slave node,
    "nodes":[
        {}
    ], # work节点的ip地址/密码 列表
}

# if gpus node existed ,noted here
gpus = []

work_temp_dir = "/tmp/k8s"

# "10.23.6.50/root"


KubernetesVersion = "1.16.15"
