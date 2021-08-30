DockerVersion=19.03.8
KubernetesVersion=1.16.15-0

cpuArch=x86_64

DownloadUrl=https://download.docker.com/linux/static/stable/${cpuArch}/docker-${DockerVersion}.tgz

# if you don't know how many version supplied by kubernetes,
# you may to use `yum list kubelet kubeadm kubectl  --showduplicates|sort -r` to get all avilable kubernetes version

.PHONY: all docker k8s rpm img rpmi clean flannel

all: docker k8s
	@echo "prepare some package"

docker:
	@echo "clean all docker binary execute file in docker file"
	rm -rf packages/docker
	@mkdir packages/docker
	@echo "down docker binary tar from network"
	curl ${DownloadUrl} -o packages/docker/docker.tar
	@echo "untar docker tar package "
	tar xf packages/docker/docker.tar -C packages/docker/
	rm -f packages/docker/docker.tar


k8s: img rpm flannel
	echo "prepare kubernetes"
	@echo "K8sVersion=$${KubernetesVersion}" >> config.py
	rm -rf packages/k8s/rpm/*
	rm -rf packages/k8s/images/
	mkdir packages/k8s/rpm
	mkdir packages/k8s/images

rpm:
	echo "prepare kubernetes repo"
	@cp packages/configure/kubernetes.repo /etc/yum.repos.d/kubernetes.repo
	@yum clean all && yum list all
	yum install kubeadm-${KubernetesVersion} kubectl-${KubernetesVersion}  kubelet-${KubernetesVersion} kubernetes-cni --downloadonly --downloaddir=packages/k8s/rpm

rpmi:
	echo "prepare kubernetes repo"
	@cp packages/configure/kubernetes.repo /etc/yum.repos.d/kubernetes.repo
	@yum clean all && yum list all
	yum install kubeadm-${KubernetesVersion} kubectl-${KubernetesVersion}  kubelet-${KubernetesVersion} kubernetes-cni -y

img:
	echo "download k8s images"
	@for img in `kubeadm config images list`;\
	do \
	  	echo $${img} && \
		newImg=`echo $${img}|sed 's@k8s.gcr.io@registry.aliyuncs.com/google_containers@'` && \
		docker pull  $${newImg} && \
		docker tag $${newImg} $${img} && \
		docker rmi $${newImg}  && \
		tagPkg=`echo $${img}|sed 's@/@-@g'|sed 's@:@-@g'` && \
		docker save $${img} -o  packages/k8s/images/$${tagPkg} ; \
	done

flannel:
	echo "download flannel images"
	@rm -rf plugins/flannel/images
	mkdir plugins/flannel/images
	docker pull quay.io/coreos/flannel:v0.11.0-arm64
	docker save quay.io/coreos/flannel:v0.11.0-arm64 -o plugins/flannel/images/flannel.tar

clean:
	echo "clean all "
	rm -f packages/k8s/rpm/*
	rm -f packages/k8s/images/*
	rm -rf packages/docker/docker
	rm -rf plugins/flannel/images/*
	@kubeadm rest -y
	yum remove kube* -y
	for img in `docker images|grep -v NAME |awk '{print $1":"$2}'`;\
	do \
		echo $${img} ;\
	done