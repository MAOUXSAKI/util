import sys, re, docker, subprocess, os,datetime
from openshift_api import OpenshiftClient,OpenshiftStatefulset
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def mkdir(path):
    import os
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False

class Properties:

    def __init__(self, file_name):
        self.file_name = file_name
        self.properties = {}
        try:
            fopen = open(self.file_name, 'r')
            for line in fopen:
                line = line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs = line.split('=')
                    self.properties[strs[0].strip()] = strs[1].strip()
        except Exception as e:
            raise e
        else:
            fopen.close()

    def has_key(self, key):
        return key in self.properties

    def get(self, key, default_value=''):
        if key in self.properties:
            return self.properties[key]
        return default_value


class Version:
    def __init__(self, ver_str, resource, target):
        if len(ver_str.split(' ')) != 2:
            pass
        name = ver_str.split(' ')[0]
        tag = ver_str.split(' ')[1]
        self.name = name
        self.tag = tag
        self.group = name.split('-')[0]
        self.resource_repository = f'{resource}/{self.group}/{self.name}'
        self.target_repository = f'{target}/{self.group}/{self.name}'


def run_shell(shell):
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

    cmd.communicate()
    return cmd.returncode


def get_version_list(file_name, resource, target):
    file = open(file_name, 'r')
    print(file.read())
    file.seek(0)
    version_str_list = file.readlines()
    filter(lambda x: x, version_str_list)
    file.close()
    version_str_list = list(map(lambda x: re.sub(r'\s+', ' ', x).strip(), version_str_list))
    version_list = []
    for version_str in version_str_list:
        if len(version_str.split(' ')) != 2:
            continue
        version = Version(version_str, resource, target)
        version_list.append(version)
    return version_list


def pull_image(version_list):
    error_list = []
    for version in version_list:
        tag = version.tag
        resource_repository = version.resource_repository
        cmd = f'docker pull {resource_repository}:{tag}'
        code = run_shell(cmd)
        if code != 0:
            error_list.append(f'{version.name} ==> {resource_repository}:{tag} pull failed ,please check this image.')

    if len(error_list) > 0:
        print('Pull has some error')
        for error in error_list:
            print(error)
    else:
        print('Pull Success')


def push_image(version_list, docker_cli):
    error_list = []
    for version in version_list:
        tag = version.tag
        resource_repository = version.resource_repository
        target_repository = version.target_repository
        docker_cli.images.get(f'{resource_repository}:{tag}').tag(f'{target_repository}:{tag}')
        cmd = f'docker push {target_repository}:{tag}'
        code = run_shell(cmd)
        if code != 0:
            error_list.append(f'{version.name} ==> {resource_repository}:{tag} push failed ,please check this image.')
        else:
            docker_cli.images.remove(f'{resource_repository}:{tag}')
    if len(error_list) > 0:
        print('Push has some error')
        for error in error_list:
            print(error)
    else:
        print('Pull Success')


def upgrade_image(version_list, config,generate):
    url = config.get('url')
    key = OpenshiftClient.get_token(url, config.get('username'), config.get('password'))
    project = config.get('project')
    openshift_cli = OpenshiftClient(url, key)
    for version in version_list:
        service_name = version.name
        tag = version.tag
        target_repository = version.target_repository
        openshift_cli.set_image(project, service_name, f'{target_repository}:{tag}')
    service_list = openshift_cli.get_statefulset_list(OpenshiftStatefulset,project_code=project)
    mkdir('version')


    if generate:
        version_file = open('version/ami-' + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M') + '.txt', 'w')
        for service in service_list:
            group = service.name.split('-')[0]
            if group in ['hes','ami']:
                version = service.pod.containers[0].image_name.split(':')[-1]
                line = f'{service.name}    \t{version}\n'
                version_file.write(line)
        version_file.close()



if __name__ == '__main__':
    config = Properties('config.properties')
    resource = config.get('resource')
    target = config.get('target')
    resource_username = config.get('resource.username')
    url = config.get('url')
    if "key" == config.get('resource.mode'):
        resource_password = OpenshiftClient.get_token(url, config.get('username'), config.get('password'))
    else:
        resource_password = config.get('resource.password')

    target_username = config.get('target.username')
    if "key" == config.get('target.mode'):
        target_password = OpenshiftClient.get_token(url, config.get('username'), config.get('password'))
    else:
        target_password = config.get('target.password')

    if len(sys.argv) < 3:
        print("Lost some param")
        os._exit(1)

    action = sys.argv[1]
    if action not in ['pull', 'push', 'update', 'all']:
        print("Action should be pull,push,upgrade,all")
        os._exit(1)

    version_file = sys.argv[2]
    if not os.path.exists(version_file):
        print(f"{version_file}: File Not Exist")
        os._exit(1)
    if 'version' != version_file.split('/')[0]:
        generate = True
    else:
        generate = False

    version_list = get_version_list(version_file, resource, target)

    if action == 'pull':
        docker_cli = docker.from_env()
        docker_cli.login(registry=resource, username=resource_username, password=resource_password)
        pull_image(version_list)
    elif action == 'push':
        docker_cli = docker.from_env()
        docker_cli.login(registry=target, username=target_username, password=target_password)
        push_image(version_list, docker_cli)
    elif action == 'update':
        upgrade_image(version_list, config,generate)
    elif action == 'all':
        docker_cli = docker.from_env()
        docker_cli.login(registry=resource, username=resource_username, password=resource_password)
        docker_cli.login(registry=target, username=target_username, password=target_password)
        pull_image(version_list)
        push_image(version_list, docker_cli)
        upgrade_image(version_list, config,generate)
