#!/ bin/python

from cus_cmd import RemoteCommand, LocalCommand
import node
from utils import ColorPrompt
import config
from commands import getstatusoutput, getoutput
import os
from utils import get_project_root_path

def install_network_plugin(plugin_name, data_iface):
    print ColorPrompt.info_prefix() +"\tBegin to install {}".format(plugin_name)
    print ColorPrompt.info_prefix() +"\tScp plugin images to all nodes"

    source_plugin_path = os.path.join(get_project_root_path(), "plugins", plugin_name)
    source_plugin_image_path = os.path.join(source_plugin_path, "images")
    remote_plugin_img_path = os.path.join(config.work_temp_dir, "plugins", plugin_name, "images")

    hosts = config.hosts
    for sighost in hosts.get("nodes" ) +hosts.get("master") + hosts.get("slave"):
        if not sighost: continue
        host ,password = sighost.get("ip"), sighost.get("password")

        RemoteCommand.security_command(host, password, "mkdir {} -pv".format(remote_plugin_img_path))
        map(lambda img: LocalCommand.scp(host, password,
                            os.path.join(source_plugin_image_path, img),
                            os.path.join(remote_plugin_img_path, img)),
            os.listdir(source_plugin_image_path))
        map(lambda img: RemoteCommand.security_command(host, password, "docker load -i {}".
                                         format(os.path.join(remote_plugin_img_path, img))),
            os.listdir(source_plugin_image_path))

    yaml_path = os.path.join(source_plugin_path, "yaml")

    if plugin_name == 'flannel':
        source_yaml = os.path.join(yaml_path, "kube-flannel.yml")
        replace = getstatusoutput("sed -i 's/DATAINTERFACE/{}/' {}".format(data_iface, source_yaml))
        yamls = [os.path.join(yaml_path, _) for _ in os.listdir(yaml_path)]
        map(lambda _: getoutput("kubectl apply -f {}".format(_)), yamls)
        undo_replace = getstatusoutput("sed -i 's/{}/DATAINTERFACE/' {}".format(data_iface, source_yaml))
    else:
        source_yaml = os.path.join(yaml_path, "calico.yaml")
        replace = getstatusoutput("sed -i 's/DATAINTERFACE/{}/' {}".format(data_iface, source_yaml))
        yamls = [os.path.join(yaml_path, _) for _ in os.listdir(yaml_path)]
        map(lambda _: getoutput("kubectl apply -f {}".format(_)), yamls)
        restore_calico = getstatusoutput("sed -i 's/{}/DATAINTERFACE/' {}".format(data_iface, source_yaml))
