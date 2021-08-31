#!/ bin/python

from cus_cmd import RemoteCommand, LocalCommand
import node
from utils import ColorPrompt
import config
from commands import getstatusoutput, getoutput
import os
from utils import get_project_root_path


class CniPlugin:
    def __init__(self, cni_name):
        self.cni_name = cni_name
        self.img_path = os.path.join(get_project_root_path(), "plugins/{}/images".format(self.cni_name))
        self.yaml_path = os.path.join(get_project_root_path(), "plugins/{}/yaml".format(self.cni_name))

    def load_cni_images(self, host, password):
        _ = RemoteCommand.security_command(host, password, "mkdir /tmp/cni/img -pv")
        map(lambda _: LocalCommand.scp(host, password, os.path.join(self.img_path, _), "/tmp/cni/img/{}".format(_)),
            os.listdir(self.img_path))

        map(lambda _: RemoteCommand.docker_load_image(host, password, "/tmp/cni/img/{}".format(_)),
            os.listdir(self.img_path))

        _ = RemoteCommand.security_command(host, password, "rm -rf /tmp/cni")

    def apply_yaml(self, data_iface):
        if self.cni_name == 'flannel':
            source_yaml = os.path.join(self.yaml_path, "kube-flannel.yml")
            replace = getstatusoutput("sed -i 's/DATAINTERFACE/{}/' {}".format(data_iface, source_yaml))
            yamls = [os.path.join(self.yaml_path, _) for _ in os.listdir(self.yaml_path)]
            undo_replace = getstatusoutput("sed -i 's/{}/DATAINTERFACE/' {}".format(data_iface, source_yaml))
        elif self.cni_name == "calico":
            source_yaml = os.path.join(self.yaml_path, "calico.yaml")
            replace = getstatusoutput("sed -i 's/DATAINTERFACE/{}/' {}".format(data_iface, source_yaml))
            yamls = [os.path.join(self.yaml_path, _) for _ in os.listdir(self.yaml_path)]
            restore_calico = getstatusoutput("sed -i 's/{}/DATAINTERFACE/' {}".format(data_iface, source_yaml))
        _ = getstatusoutput("kubectl apply -f {}/".format(self.yaml_path))