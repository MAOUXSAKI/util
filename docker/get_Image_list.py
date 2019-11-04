import requests
import json
import traceback
import warnings
import sys
import docker

warnings.filterwarnings("ignore")

repo_ip = '10.32.233.112'

def getImagesNames(repo_ip,project_name=None):
    docker_images = []
    try:
        url = "https://" + repo_ip + "/api/projects"
        print(url)
        res =requests.get(url,verify=False, auth=('admin','kaifa123')).text.strip()
        res_dic = json.loads(res)
        for j in res_dic:
            if project_name != None and j['name'] != project_name :
                continue
            repositoriesUrl = "http://" + repo_ip +"/api/repositories?project_id=" + str(j['project_id'])
            headers = {"Accept":"application/json"}
            repositoriesStr = requests.get(repositoriesUrl,verify=False, headers=headers, auth=('admin','kaifa123')).text.strip()
            repositories = json.loads(repositoriesStr)
            for repository in repositories:
                tagUrl = "http://" + repo_ip +"/api/repositories/" + repository['name'] +"/tags"
                tagsStr = requests.get(tagUrl,verify=False, headers=headers, auth=('admin','kaifa123')).text.strip()
                tags = json.loads(tagsStr)
                for tag in tags:
                    images_name = str(repo_ip) + "/" + repository['name'] + ":" + tag['name'] + '\n'
                    docker_images.append(images_name)
    except:
        traceback.print_exc()
    return docker_images


if len(sys.argv) == 1 or sys.argv[1] == 'list':
    if len(sys.argv) > 2:
        project_name = sys.argv[2]
    else
        project_name = None
    docker_images = getImagesNames(repo_ip,project_name)
    f1 = open('docker_images.txt','w')
    f1.writelines(docker_images)
    for image in docker_images:
        print(image.strip())
    print(len(docker_images))
elif sys.argv[1] == 'pull':
    f1 = open('docker_images.txt','r')
    docker_images = f1.readlines()
    client1 = docker.from_env()
    count = 0
    for image in docker_images:
        count = count + 1
        print(count)
        client1.images.pull(image.strip())
    f1.close()
