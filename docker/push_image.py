import requests
import json
import traceback
import warnings
import sys
import docker

warnings.filterwarnings("ignore")

repo_ip = '10.32.233.112'

f1 = open('docker_images.txt','r')
docker_images = f1.readlines()
client = docker.from_env()
for image in docker_images:
    print('----push '+image+'start ----')
    client.images.push(image.strip())
    print('----push '+image+'end   ----')
    client.images.remove(image.strip())
f1.close()