# 说明
&emsp;此脚本是用于离线安装，需要用户提前在一个有网络的环境执行make all来准备好所有需要的软件包，最终生成一个完整的离线安装包， 下面步骤演示如何在一个有网络的环境制作离线安装包

# support os
>note：目前在Euler制作的一件安装包，在下列操作系统上测试部署kubernetes， 其他的centos7.X理论上也支持，但是暂未全部挨个测试.

|云厂商|操作系统版本|是否支持|
|----|----|----|
|华为|Euler-2.2|支持|
|华为|Centos-7.2|支持|
|华为|Centos-7.6|支持|
|阿里云|Centos-7.2|支持|
|阿里云|Centos-7.6|支持|
|阿里云|Centos-7.9|支持|
|腾讯云|Centos-7.2|支持|
|腾讯云|Centos-7.6|支持|
|腾讯云|Centos-7.9|支持|
|AWS|amazon v2|支持|
|谷歌云|centos7.9|支持|



## 0x00 制作离线安装包
# get install package
```bash
git clone https://github.com/clickpaas/k8s-offline-install.git
```

> note：制作离线安装包阶段需要有网/有docker
```bash
cd k8s-offline-install
make all

cd ..
tar cf k8s-offline-install
```


## 0x01 当制作完成离线安装包就可以拿着离线安装包到客户/无网络环境安装k8s

## 手动安装
&emsp;客户环境不支持scp,需要每个节点都单独安装
#### 修改配置文件
vim config.py
```python
hosts = {
    "master": [
        {"ip": "172.17.0.2", "user": "root", "password": "xxxxxxx"}, # 这里随便乱填写一个就可以
    ],
    "slave": [
    ],
    "nodes": [
        # 不填写
    ],
SupportScpTransform = False  # 设置设置为Fasle, 禁用远程ssh scp功能,全部采用本地直接命令执行
}
```

#### 将离线修改好的离线安装包copy到所有的节点
```bash
# 所有的节点都执行安装
python install.py

# 执行安装完成后,执行reset
kubeadm reset
```

#### 手动创建hosts解析(所有节点都执行)
```bash
echo "第一个节点ip kubernetes.default " >> /etc/hosts
# echo "$(hostname -i) kubernetes.default " >> /etc/hosts
```

#### master执行init
```bash
./kubeadm init  --kubernetes-version=1.16.15 --pod-network-cidr=10.244.0.0/16  --control-plane-endpoint kubernetes.default --upload-certs

ot@ali-jkt-dc-risk-pwc-ecl-prod01 k8s-offline-1.16]#
[root@ali-jkt-dc-risk-pwc-ecl-prod01 k8s-offline-1.16]# ./kubeadm init  --kubernetes-version=1.16.15 --pod-network-cidr=10.244.0.0/16  --control-plane-endpoint kubernetes.default --upload-certs
.........# 省略
Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

You can now join any number of the control-plane node running the following command on each as root:

# 这个copy下在另外两个master上执行
  kubeadm join kubernetes.default:6443 --token rcklh9.nso0fk3fxbzoxul8 \
    --discovery-token-ca-cert-hash sha256:2fa04b82769a6f8360c8378a6ffde3c0bce4281d57eb54f55912ddb7ff233651 \
    --control-plane --certificate-key 001aa1396ec3392b20158ea9c7f2114c6561222f7a584cd97c2f93848ec863f2

Please note that the certificate-key gives access to cluster sensitive data, keep it secret!
As a safeguard, uploaded-certs will be deleted in two hours; If necessary, you can use
"kubeadm init phase upload-certs --upload-certs" to reload certs afterward.

Then you can join any number of worker nodes by running the following on each as root:

# 这个在work节点上执行
kubeadm join kubernetes.default:6443 --token rcklh9.nso0fk3fxbzoxul8 \
    --discovery-token-ca-cert-hash sha256:2fa04b82769a6f8360c8378a6ffde3c0bce4281d57eb54f55912ddb7ff233651
[root@ali-jkt-dc-risk-pwc-ecl-prod01 k8s-offline-1.16]#

```

#### 创建kubeconfig配置文件(在master节点)
```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

#### slave节点执行join命令
在另外的master上执行join命令
```bash
# 这里只是例子，具体的join命令还需要根基实际上面输出
kubeadm join kubernetes.default:6443 --token rcklh9.nso0fk3fxbzoxul8 \
    --discovery-token-ca-cert-hash sha256:2fa04b82769a6f8360c8378a6ffde3c0bce4281d57eb54f55912ddb7ff233651 \
    --control-plane --certificate-key 001aa1396ec3392b20158ea9c7f2114c6561222f7a584cd97c2f93848ec863f2
```


#### work节点执行join命令
在work节点上执行
```bash
# 这里只是例子，具体的join命令还需要根基实际上面输出
kubeadm join kubernetes.default:6443 --token rcklh9.nso0fk3fxbzoxul8 \
    --discovery-token-ca-cert-hash sha256:2fa04b82769a6f8360c8378a6ffde3c0bce4281d57eb54f55912ddb7ff233651
```

#### 让master设置为可以调度
```bash
kubectl taint nodes --all node-role.kubernetes.io/master-
```

#### 安装网络插件
```bash
kubectl apply -f plugins/flannel/yaml/kube-flannel.yaml
```

## 自动一键安装

#### 配置文件
```bash
hosts = {
    "master": [
        {"ip": "172.17.0.2", "user": "root", "password": "xxxxxxx"},        # 第一台master的信息
    ],  # master节点的ip地址/密码
    "slave": [
        # 如果有多台master的话，其余master配置到slave里面
        {"ip": "172.17.0.2", "user": "root", "password": "xxxxxxx"},        # 第二台master的信息
        {"ip": "172.17.0.2", "user": "root", "password": "xxxxxxx"},        # 第三台master的信息
    ],  # slave node,
    "nodes": [
        # 如果没有node节点则不填, 设置为空 {}
        {"ip": "", "user":"root", "password": "xxxx"},                      # worker节点信息
    ],  # work节点的ip地址/密码 列表
}

SupportScpTransform = True
SupportFormatHostname = True        # 是否要格式化节点名称(如果当前主机名为localhost之类,建议设置为True)
```

#### 开始执行一键安装
```bash
python install.py
```

#### 让master设置为可以调度
```bash
kubectl taint nodes --all node-role.kubernetes.io/master-


### Donate
&emsp;If it helps you, you can buy me a coffue if you want.<br/>
<img src="https://github.com/clickpaas/k8s-offline-install/blob/main/image/wechat.jpeg" width="200px" height="200px" />
<img src="https://github.com/clickpaas/k8s-offline-install/blob/main/image/alipay.jpeg" width="200px" height="200px" />
