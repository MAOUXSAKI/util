import requests
import json
import traceback
import warnings
import sys
import docker

warnings.filterwarnings("ignore")

repo_ip = 'image.kaifa-empower.com'

f1 = open('docker_images.txt','r')
docker_images = f1.readlines()
client = docker.from_env()
save_name_list = []
for image_name in docker_images:
    real_name = image_name.strip().split('/',1)[1]
    image = client.images.get(image_name.strip())
    image.tag(repo_ip + '/'+real_name)
    save_name_list.append( repo_ip + '/'+real_name)
for image in save_name_list:
    print('----push '+image+'start ----')
    client.images.push(image.strip())


for image_name in docker_images:
    client.images.remove(image_name.strip())

for real_name in save_name_list:
    client.images.remove(real_name)


f1.close()
