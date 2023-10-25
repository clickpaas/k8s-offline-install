#!/ bin/python

from common.cus_cmd import RemoteCommand, LocalCommand

import os
from common.utils import get_project_root_path, general_syscmd_execute


class K8sOperator:
    def __init__(self):
        self.yaml_path = os.path.join(get_project_root_path(), "operator/yaml")
        self.img_path = os.path.join(get_project_root_path(), "operator/img")

    def load_cni_images(self, host, password):
        _ = RemoteCommand.security_command(host, password, "mkdir /tmp/operator/img -pv")
        list(
            map(lambda _: LocalCommand.scp(host, password, os.path.join(self.img_path, _), "/tmp/operator/img/{}".format(_)),
                os.listdir(self.img_path)))

        list(map(lambda _: RemoteCommand.docker_load_image(host, password, "/tmp/operator/img/{}".format(_)),
                 os.listdir(self.img_path)))

        _ = RemoteCommand.security_command(host, password, "rm -rf /tmp/operator")

    def apply_yaml(self):
        yamls = [os.path.join(self.yaml_path, _) for _ in os.listdir(self.yaml_path)]
        _ = general_syscmd_execute("kubectl apply -f {}/".format(self.yaml_path))
