from collections import OrderedDict
import yaml


def mkdir(path):
    import os
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


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


if __name__ == '__main__':
    mkdir('docker-compose')
    config_yml = ordered_yaml_load("config.yml")
    docker_compose_file = open("docker-compose/docker-compose.yml", "w")

    print(config_yml)

    docker_compose = OrderedDict()
    docker_compose['version'] = '2.4'

    time_zone = config_yml['tz']
    project = config_yml['project']

    web_services = config_yml['web']['services']

    services = OrderedDict()

    for k, v in web_services.items():
        tag = str(v['tag'])
        environment_list = []
        environment_list.append('TZ=' + time_zone)
        service = OrderedDict()
        if k == 'web':
            service['image'] = '10.32.233.112/ami/ami-web:' + tag
            if 'config-dir' in v:
                service['volumes'] = [v['config-dir'] + ':/etc/properties']
        else:
            if k != 'config' and k != 'register':
                depends_on = OrderedDict()
                depends_on['register-service'] = {"condition": "service_healthy"}
                depends_on['config-service'] = {"condition": "service_healthy"}
                service['depends_on'] = depends_on
            else:
                if k == 'config':
                    depends_on = OrderedDict()
                    depends_on['register-service'] = {"condition": "service_healthy"}
                    service['depends_on'] = depends_on
                health_check = OrderedDict()
                health_check['test'] = "netstat -tupan | grep LISTEN | grep 8880 && exit 0 || exit 1"
                health_check['timeout'] = "5s"
                health_check['retries'] = 10
                health_check['interval'] = "20s"
                health_check['start_period'] = "10s"
                service['healthcheck'] = health_check
            service['image'] = '10.32.233.112/ami/ami-api-' + k + '-service:' + tag
            if 'config-dir' in v:
                service['volumes'] = [v['config-dir'] + ':/etc/properties']
            if 'project' in v:
                environment_list.append('PROJECT=' + v['project'])
            else:
                environment_list.append('PROJECT=' + project)
            if 'memory' in v:
                environment_list.append('XMX_SIZE=' + v['memory'])
            else:
                environment_list.append('XMX_SIZE=512m')
        service['environment'] = environment_list
        if 'port' in v:
            service['ports'] = [str(v['port']) + ':8080']
        service['restart'] = 'always'
        services[k + '-service'] = service

    docker_compose['services'] = services

    ordered_yaml_dump(docker_compose, docker_compose_file)
    docker_compose_file.close()
