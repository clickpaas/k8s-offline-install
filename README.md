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

### 0x00 修改相对应的配置文件
```bash
vi config.py  # 编辑配置文件
# coding:utf-8
hosts = {
    "master": [
        {"ip": "10.77.13.208", "user": "root", "password": "Abcd@123"},
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

# 指定k8s版本，这个版本信息需要和Makefile里面的保持一致
# 假设Makefile里面指定的版本上1.16.15-0 ， 那么这个里面就需要写1.16.15   (注意后面没有-0）
KubernetesVersion = "1.16.15"
```

### 0x01 执行安装
&emsp;根据引导一步步安装k8s(网络插件目前只支持flannel）
```bash
python install.py
```

### Donate
&emsp;If it helps you, you can buy me a coffue if you want.<br/>
<img src="https://github.com/clickpaas/k8s-offline-install/blob/master/image/wechat.jpeg" width="200px" height="200px" />
<img src="https://github.com/clickpaas/k8s-offline-install/blob/master/image/alipay.jpeg" width="200px" height="200px" />
