#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from owncloud import Client

from os import environ

from sys import argv


class OwncloudUpload:
    """
    上传文件到owncloud网盘脚本
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

         # 网址
        if 'OWN_CLOUD_URL' in environ :
            self.url = environ['OWN_CLOUD_URL']
        else:
            self.url = 'http://10.32.233.231:8080'

        # 用户名
        if 'OWN_CLOUD_USERNAME' in environ :
            self.username = environ['OWN_CLOUD_USERNAME']
        else:
            self.username = 'deployment'

        # 密码    
        if 'OWN_CLOUD_PASSWORD' in environ :
            self.password = environ['OWN_CLOUD_PASSWORD']
        else:
            self.password = 'deployment'
        

    def upload(self,fold,upload_file):

        owncloud_client = self.login()
        fold = fold + '/'
        # 上传文件
        print('Upload fold is {}.'.format(fold))
        self.upload_file(owncloud_client, fold, upload_file)

    def login(self):
        """
        登录网盘
        :return: 返回owncloud链接对象
        """
        try:
            owncloud_client = Client(self.url)
            owncloud_client.login(self.username, self.password)
            print('Login success.')
        except Exception as e:
            print('Login failed. HTTP error is: {}'.format(e))

        return owncloud_client

    @staticmethod
    def upload_file(oc, fold, file):
        """
        上传文件
        :param oc: owncloud_client对象
        :param fold: 目标文件夹
        :param file: 被上传的文件
        :return: None
        """
        try:
            oc.put_file(fold, file)
            print('Upload {} success.'.format(file))
        except Exception as e:
            print('Upload {} failed. HTTP error is: {}'.format(file, e))

if __name__ == "__main__":
    dic = argv[2]
    #被上传的文件
    upload_file = argv[1]
    client = OwncloudUpload()
    client.upload(dic,upload_file)