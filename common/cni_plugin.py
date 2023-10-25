#!/ bin/python

from common.cus_cmd import RemoteCommand, LocalCommand

import os
from common.utils import get_project_root_path, general_syscmd_execute


class CniPlugin:
    def __init__(self, cni_name):
        self.cni_name = cni_name
        self.img_path = os.path.join(get_project_root_path(), "plugins/{}/images".format(self.cni_name))
        self.yaml_path = os.path.join(get_project_root_path(), "plugins/{}/yaml".format(self.cni_name))

    def load_cni_images(self, host, password):
        _ = RemoteCommand.security_command(host, password, "mkdir /tmp/cni/img -pv")
        list(
            map(lambda _: LocalCommand.scp(host, password, os.path.join(self.img_path, _), "/tmp/cni/img/{}".format(_)),
                os.listdir(self.img_path)))

        list(map(lambda _: RemoteCommand.docker_load_image(host, password, "/tmp/cni/img/{}".format(_)),
                 os.listdir(self.img_path)))

        _ = RemoteCommand.security_command(host, password, "rm -rf /tmp/cni")

    def apply_yaml(self, data_iface):
        source_yaml = ""
        if self.cni_name == 'flannel':
            source_yaml = os.path.join(self.yaml_path, "kube-flannel.yml")
        elif self.cni_name == "calico":
            source_yaml = os.path.join(self.yaml_path, "calico.yaml")
        # replace = general_syscmd_execute("sed -i 's/DATAINTERFACE/{}/' {}".format(data_iface, source_yaml))
        # yamls = [os.path.join(self.yaml_path, _) for _ in os.listdir(self.yaml_path)]
        _ = general_syscmd_execute("kubectl apply -f {}/".format(self.yaml_path))
        # undo_replace = general_syscmd_execute("sed -i 's/{}/DATAINTERFACE/' {}".format(data_iface, source_yaml))
