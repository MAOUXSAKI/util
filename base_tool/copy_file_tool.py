import os, shutil


def mymovefile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        return
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.move(srcfile, dstfile)  # 移动文件


def copy_file(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        return
    if os.path.isfile(dstfile):
        return
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.copyfile(srcfile, dstfile)  # 复制文件
