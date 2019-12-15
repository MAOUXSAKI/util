from collections import OrderedDict
import yaml
import shutil
import os

environment_config_list = {
    "DEV": "http://10.32.233.112:8080",
    "QA": "http://10.32.233.112:8081",
    "UAT": "http://10.32.233.112:8082",
    "CLOUD": "http://10.0.0.20:8080"
}

environment_ip_list = {
    "DEV": "http://10.32.233.12",
    "QA": "http://10.32.233.31"
}

environment_url_list = {
    "DEV": ".kaifa.develop",
    "QA": ".kaifa.tst"
}


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


def remove_dir(path):
    isExists = os.path.exists(path)
    if not isExists:
        return False
    else:
        shutil.rmtree("target")
        return True


def ordered_yaml_load(yaml_path, Loader=yaml.Loader,
                      object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    with open(yaml_path) as stream:
        return yaml.load(stream, OrderedLoader)


def ordered_yaml_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def replace(file_path, old_str, new_str):
    try:
        f = open(file_path, 'r+')
        all_lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in all_lines:
            line = line.replace(old_str, new_str)
            f.write(line)
        f.close()
    except Exception as e:
        print(e)


class Service:
    def __init__(self):
        self.repository = ""
        self.code = ""
        self.name = ""
        self.tag = ""
        self.image = ""
        self.project = ""
        self.project_template = ""
        self.time_zone = "Asia/Shanghai"
        self.memory = "512m"
        self.port = ""
        self.config_mode = ""
        self.config = ""
        self.volumes = []
        self.namespace = ""
        self.apollo_meta = ""

    def set_info(self, code, data):
        self.code = code
        if code != "web":
            self.name = "api-" + code + "-service"
        else:
            self.name = code
        if "port" in data:
            self.port = data["port"]
        if "config-dir" in data:
            self.config = data["config-dir"]
        if 'tag' in data:
            self.tag = data['tag']
        self.image = self.repository + "/ami/ami-" + self.name + ":" + str(self.tag)
        if 'memory' in data:
            self.memory = data['memory']
        if 'project_template' in data:
            self.project_template = data['project_template']
        elif 'project' in data:
            self.project_template = data['project']
        if "volumes" in data:
            self.volumes = data['volumes']

    def generate_openshift_file(self):
        target_file_name = "target/ami-" + self.name + ".yml"
        service_file_name = "target/service-" + self.name + ".yml"
        if self.port != "":
            shutil.copyfile("template/service_template.yml", service_file_name)
            replace(service_file_name,"@PORT@",str(self.port))
            replace(service_file_name, "@NAME@", self.name)
        if self.code == "web":
            shutil.copyfile("template/web_template.yml",target_file_name)
            replace("target/ami-web.yml", "@IMAGE@", self.image)
            replace("target/ami-web.yml", "@TIME_ZONE@", self.time_zone)
        else:
            if self.code == "config":
                shutil.copyfile("template/config_template.yml", target_file_name)
            else:
                shutil.copyfile("template/template.yml", target_file_name)
            if self.code == "gateway":
                replace("target/web-config-map.yml", "@PORT@", str(self.port))
            replace(target_file_name, "@IMAGE@", self.image)
            replace(target_file_name, "@MEMORY@", self.memory)
            replace(target_file_name, "@NAME@", self.name)
            replace(target_file_name, "@TIME_ZONE@", self.time_zone)
            replace(target_file_name, "@CONFIG_MODE@", self.config_mode)
            replace(target_file_name, "@PROJECT@", self.project_template)
            replace(target_file_name, "@APOLLO_PROJECT@", "ami")
            replace(target_file_name, "@NAMESPACE@", self.namespace)
            replace(target_file_name, "@PROJECT_CLUSTER@", self.project)
            replace(target_file_name, "@APOLLO_META@", self.apollo_meta)


class Project:
    def __init__(self, config=None):
        if config is None:
            self.project = ""
            self.time_zone = ""
            self.project_template = ""
            self.service_list = []
            self.config_mode = ""
            self.namespace = ""
            self.apollo_meta = ""
            self.env = ""
        else:
            self.project = config['project']
            if 'project_template' in config:
                self.project_template = config['project_template']
            else:
                self.project_template = self.project
            if 'config_mode' in config:
                self.config_mode = config['config_mode']
            else:
                self.config_mode = "cloud-config"
            if 'repository' in config:
                self.repository = config['repository']
            else:
                self.repository = "image.kaifa-empower.com"
            if 'namespace' in config:
                self.namespace = config['namespace']
            else:
                self.namespace = "infrastructure,dateformat,external-api,web-other"
            if 'env' in config:
                self.env = config['env']
            else:
                self.env = "DEV"

            if 'apollo_meta' in config:
                self.apollo_meta = config['apollo_meta']
            else:
                self.apollo_meta = environment_config_list[self.env]

            self.time_zone = config['tz']
            self.web = config['web']
            self.service_list = []
            for k, v in self.web['services'].items():
                service = Service()
                service.apollo_meta = self.apollo_meta
                service.repository = self.repository
                service.project = self.project
                service.project_template = self.project_template
                service.time_zone = self.time_zone
                service.config_mode = self.config_mode
                service.namespace = self.namespace
                service.set_info(k, v)
                self.service_list.append(service)

    def generate_openshift_file(self):
        remove_dir("target")
        mkdir("target")
        shutil.copyfile("template/web-config-map.yml", "target/web-config-map.yml")
        shutil.copyfile("template/web-router.yml", "target/web-router.yml")
        replace("target/web-config-map.yml","@ENVIRONMENT_IP@",environment_ip_list[self.env])
        replace("target/web-router.yml","@HOST@",self.project + environment_url_list[self.env])
        shutil.copyfile("template/service.yml", "target/service.yml")
        for service in self.service_list:
            service.generate_openshift_file()


config_yml = ordered_yaml_load("config.yml")
project = Project(config_yml)
project.generate_openshift_file()
