import requests, enum, json,re


def parse(function):
    def parse_result(self, clazz=None, *args, **kwargs):
        data = function(self, *args, **kwargs)

        if clazz is not None:
            if isinstance(data, list):
                result = []
                for temp in data:
                    result.append(clazz.parse(temp))
            else:
                result = clazz.parse(data)
        else:
            if isinstance(data, list):
                OpenshiftClient.remove_list_resource_version(data)
            else:
                OpenshiftClient.remove_resource_version(data)
            result = data
        return result

    return parse_result


class OpenshiftClient:
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.headers = {'Authorization': 'Bearer %s' % self.key, 'Content-Type': 'application/json'}

    statefulset_url = '%s/apis/apps/v1beta1/namespaces/%s/statefulsets/%s'
    statefulset_list_url = '%s/apis/apps/v1beta1/namespaces/%s/statefulsets'
    service_list_url = '%s/api/v1/namespaces/%s/services'
    pod_list_url = '%s/api/v1/namespaces/%s/pods'
    pod_url = '%s/api/v1/namespaces/%s/pods/%s'

    @staticmethod
    def remove_resource_version(json_data):
        json_data.get('metadata').pop('resourceVersion')

    @staticmethod
    def get_token(url,username,password):
        session = requests.session()
        session.auth = (username, password)
        session.headers = {"X-CSRF-Token": "1", 'Content-Type': 'application/x-www-form-urlencoded'}
        response = session.get(
            f'{url}/oauth/authorize?client_id=openshift-challenging-client&response_type=token',
            verify=False, allow_redirects=False)
        location = response.headers['Location']
        return re.findall(r'access_token=(.+?)&', location)[0]


    @staticmethod
    def remove_list_resource_version(json_data_list):
        for json_data in json_data_list:
            json_data.get('metadata').pop('resourceVersion')

    @parse
    def get_statefulset(self, project_code, service_code):
        statefulset_url = OpenshiftClient.statefulset_url % (self.url, project_code, service_code)
        result = requests.get(statefulset_url, headers=self.headers, verify=False).json()
        if result.get('code'):
            raise Exception(result.get('message'))
        else:
            return result

    def set_image(self, project_code, service_code, image):
        statefulset = self.get_statefulset(None, project_code, service_code)
        spec = statefulset.get('spec')
        replicas = spec['replicas']
        containers = spec.get('template').get('spec').get('containers')
        if containers[0]['image'] == image:
            return 201
        else:
            containers[0]['image'] = image
        statefulset_url = OpenshiftClient.statefulset_url % (self.url, project_code, service_code)
        result = requests.put(statefulset_url, data=json.dumps(statefulset), headers=self.headers, verify=False).json()
        if result.get('code'):
            raise Exception(result.get('message'))
        if replicas > 0:
            self.delete_service_pod_by_statefulset(project_code, statefulset)
        return 200

    @parse
    def get_service_list(self, project_code):
        service_list_url = OpenshiftClient.service_list_url % (self.url, project_code)
        result = requests.get(service_list_url, headers=self.headers, verify=False).json()
        if result.get('code'):
            raise Exception(result.get('message'))
        else:
            return result.get('items')

    @parse
    def get_statefulset_list(self, project_code):
        statefulset_list_url = OpenshiftClient.statefulset_list_url % (self.url, project_code)
        result = requests.get(statefulset_list_url, headers=self.headers, verify=False).json()
        if result.get('code'):
            raise result.get('message')
        else:
            return result.get('items')

    def set_statefulset_replicas(self, project_code, service_code, replicas):
        statefulset = self.get_statefulset(None, project_code, service_code)
        statefulset.get('spec')['replicas'] = replicas
        statefulset_url = OpenshiftClient.statefulset_url % (self.url, project_code, service_code)
        result = requests.put(statefulset_url, data=json.dumps(statefulset), headers=self.headers, verify=False).json()
        if result.get('code'):
            raise Exception(result.get('message'))

    def delete_service_pod(self, project_code, service_code):
        statefulset = self.get_statefulset(OpenshiftStatefulset, project_code, service_code)
        self.delete_service_pod_by_statefulset(project_code, statefulset)

    def delete_service_pod_by_statefulset(self, project_code, statefulset):
        selector = ""
        if not isinstance(statefulset,OpenshiftStatefulset):
            statefulset = OpenshiftStatefulset.parse(statefulset)
        for k, v in statefulset.pod.labels.items():
            selector = selector + "%s=%s," % (k, v)
        selector = selector.strip(',')
        pod_list_url = OpenshiftClient.pod_list_url % (self.url, project_code)
        result = requests.get(pod_list_url, params={"labelSelector": selector}, headers=self.headers,
                              verify=False).json()
        pod_list = result.get('items')
        pod_name_list = map(lambda x: x.get('metadata').get('name'), pod_list)
        for pod_name in pod_name_list:
            pod_url = OpenshiftClient.pod_url % (self.url, project_code, pod_name)
            data = {"gracePeriodSeconds": 0}
            requests.delete(pod_url, data=json.dumps(data), headers=self.headers, verify=False)


class OpenshiftServiceType(enum.Enum):
    NODE_PORT = 'NodePort'
    CLUSTER_IP = 'ClusterIP'


class OpenshiftService:
    def __init__(self):
        self.name = ''
        self.selector = ''
        self.type = ''
        self.ports = []

    @staticmethod
    def parse(json_data):
        root_metadata = json_data.get('metadata')
        root_spec = json_data.get('spec')

        service = OpenshiftService()
        service.name = root_metadata.get('name')
        service.ports = root_spec.get('ports')
        service.selector = root_spec.get('selector')
        service.type = OpenshiftServiceType(root_spec.get('type'))
        return service


class OpenshiftContainer:
    def __init__(self):
        self.name = ''
        self.image_name = ''
        self.tag = ''
        self.image = ''


class OpenshiftPod:
    def __init__(self):
        self.labels = {}
        self.containers = []


class OpenshiftStatefulset:
    def __init__(self):
        self.name = ''
        self.pod: OpenshiftPod = OpenshiftPod()
        self.replicas = 0
        self.labels = {}

    @staticmethod
    def parse(json_data):
        statefulset = OpenshiftStatefulset()

        root_metadata = json_data.get('metadata')
        root_spec = json_data.get('spec')
        statefulset.name = root_metadata.get('name')
        statefulset.labels = root_metadata.get('labels')
        statefulset.replicas = root_spec.get('replicas')

        template = root_spec.get('template')
        template_metadata = template.get('metadata')
        template_spec = template.get('spec')
        statefulset.pod.labels = template_metadata.get('labels')

        for container_t in template_spec.get('containers'):
            container = OpenshiftContainer()
            container.name = container_t.get('name')
            image_name = container_t.get('image')
            container.image_name = image_name
            container.tag = image_name.split(':')[1]
            container.image = image_name.split(':')[0].split('/')[-1]
            statefulset.pod.containers.append(container)
        return statefulset
