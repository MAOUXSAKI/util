import uuid, os, json
from pathlib import Path


def exec_shell(shell, param='{"data":"ok"}'):
    result_path = os.path.join(os.path.dirname(__file__), 'result')
    shell_path = os.path.join(os.path.dirname(__file__), 'shell')
    json_param = json.dumps(json.dumps(param))
    id = str(uuid.uuid1())
    result_path = Path(os.path.join(result_path,id)).as_posix()
    shell_path = Path(os.path.join(shell_path,'exec_shell.sh')).as_posix()
    shell = "bash " + shell_path + " %s %s %s" % (shell,json_param, result_path)
    os.system(shell)
    result_file = open(result_path,'r',encoding='utf-8')
    result = json.load(result_file)
    result_file.close()
    if result['code'] != 200:
        os.remove(result_path)
        raise result['data']
    os.remove(result_path)
    return result['data']


if __name__ == '__main__':
    exec_shell('shell/service_tag_list.sh')