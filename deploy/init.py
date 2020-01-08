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
    with open(yaml_path, encoding='UTF-8') as stream:
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


def generate_hes(data):
    hes_services = OrderedDict()
    hes_repository = repository + '/hes'
    for k, v in data.items():
        environment_list = []
        environment_list.append('TZ=' + time_zone)
        environment_list.append('CONFIG=LOCAL')
        service = OrderedDict()
        tag = v.get('tag', 'latest')
        port = v.get('port', None)
        config_dir = v.get('config-dir', None)
        hostname = v.get('hostname', 'hes')
        service['image'] = hes_repository + '/' + k + ':' + str(tag)
        service['restart'] = 'always'
        service['hostname'] = hostname
        if port:
            service['ports'] = [str(port) + ':8080']
        service['environment'] = environment_list
        if config_dir:
            service['volumes'] = [config_dir]
        hes_services[k] = service
    return hes_services


if __name__ == '__main__':
    mkdir('ami')
    config_yml = ordered_yaml_load("config.yml")
    docker_compose_file = open("ami/docker-compose.yml", "w")

    docker_compose = OrderedDict()
    docker_compose['version'] = '2.3'

    time_zone = config_yml['tz']
    project = config_yml['project']
    if 'project_template' in config_yml:
        project_template = config_yml['project_template']
    else:
        project_template = project
    repository = config_yml['repository']
    if 'config_mode' in config_yml:
        config_mode = config_yml['config_mode']
    else:
        config_mode = 'cloud-config'

    if 'namespace' in config_yml:
        namespace = config_yml['namespace']
    else:
        namespace = 'infrastructure,dateformat,external-api,web-other'

    web_services = config_yml['web']['services']

    hes = config_yml.get('hes', None)

    tag = str(config_yml['web']['tag'])

    services = OrderedDict()

    for k, v in web_services.items():
        if 'tag' in v:
            tag = str(v['tag'])
        environment_list = []
        environment_list.append('TZ=' + time_zone)
        service = OrderedDict()
        if k == 'web':
            service['image'] = repository + '/ami/ami-web:' + tag
            if 'config-dir' in v:
                service['volumes'] = [v['config-dir'] + ':/etc/properties']
        else:
            if k != 'config' and k != 'register':
                depends_on = OrderedDict()
                depends_on['register-service'] = {"condition": "service_healthy"}
                environment_list.append('CONFIG=' + config_mode)
                if config_mode != 'apollo':
                    depends_on['config-service'] = {"condition": "service_healthy"}
                else:
                    environment_list.append('NAMESPACE=' + namespace)
                    environment_list.append('JAVA_OPT=-Dapollo.bootstrap.namespaces=' + namespace)
                    environment_list.append('APOLLO_PROJECT=' + project)
                service['depends_on'] = depends_on
            else:
                if k == 'config':
                    depends_on = OrderedDict()
                    depends_on['register-service'] = {"condition": "service_healthy"}
                    service['depends_on'] = depends_on
                health_check = OrderedDict()
                health_check['test'] = "netstat -tupan | grep LISTEN | grep 8080 && exit 0 || exit 1"
                health_check['timeout'] = "10s"
                health_check['retries'] = 10
                health_check['interval'] = "20s"
                health_check['start_period'] = "10s"
                service['healthcheck'] = health_check
            service['image'] = repository + '/ami/ami-api-' + k + '-service:' + tag

            if 'config-dir' in v:
                service['volumes'] = [v['config-dir'] + ':/etc/properties']
            if 'project_template' in v:
                environment_list.append('PROJECT=' + v['project_template'])
            else:
                environment_list.append('PROJECT=' + project_template)
            if 'memory' in v:
                environment_list.append('XMX_SIZE=' + v['memory'])
            else:
                environment_list.append('XMX_SIZE=512m')
        service['environment'] = environment_list
        if 'port' in v:
            service['ports'] = [str(v['port']) + ':8080']
        service['restart'] = 'always'
        services[k + '-service'] = service

    if hes:
        services.update(generate_hes(hes['services']))

    docker_compose['services'] = services

    ordered_yaml_dump(docker_compose, docker_compose_file)
    docker_compose_file.close()
