import os, shutil, sys
from base_tool import global_var as gl


def move_file(srcfile, dstfile):
    srcfile = file_dir(srcfile)
    dstfile = file_dir(dstfile)
    if not os.path.isfile(srcfile):
        return
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.move(srcfile, dstfile)  # 移动文件


def copy_file(srcfile, dstfile, force=False):
    srcfile = file_dir(srcfile)
    dstfile = dstfile
    if not os.path.isfile(srcfile):
        return
    if os.path.isfile(dstfile) and not force:
        return
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.copyfile(srcfile, dstfile)  # 复制文件


def file_dir(file_name):
    base_dir = gl.get_value('project.dir')
    if file_name is not None and '/' in file_name:
        file_name = file_name.split('/')
        for file in file_name:
            base_dir = os.path.join(base_dir, file)
    else:
        base_dir = os.path.join(base_dir, file_name)
    return base_dir

def get_document_dir():
    return  os.path.join(os.path.expanduser('~'),'Documents')

def set_project_dir():
    gl.set_value('project.dir',os.path.dirname(os.path.abspath(sys.argv[0])))


def replace_file_content(file, old_str, new_str, s=1):
    file = file_dir(file)
    with open(file, "r", encoding="utf-8") as f:
        # readlines以列表的形式将文件读出
        lines = f.readlines()

    with open(file, "w", encoding="utf-8") as f_w:
        # 定义一个数字，用来记录在读取文件时在列表中的位置
        n = 0
        # 默认选项，只替换第一次匹配到的行中的字符串
        if s == 1:
            for line in lines:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                    f_w.write(line)
                    n += 1
                    break
                f_w.write(line)
                n += 1
            # 将剩余的文本内容继续输出
            for i in range(n, len(lines)):
                f_w.write(lines[i])
        # 全局匹配替换
        elif s == 'g':
            for line in lines:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                f_w.write(line)
        elif s == 'd':
            for line in lines:
                if old_str in line:
                    line = new_str + '\n'
                f_w.write(line)
