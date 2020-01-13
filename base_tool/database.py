from base_tool import global_var as gl
from base_tool.file_tool import file_dir

import atexit

class DataBaseData:
    pass


def get_dict_list(cursor):
    fields = [d[0].lower() for d in cursor.description]
    rst = cursor.fetchall()
    if rst:
        result = [dict(zip(fields, row)) for row in rst]
        return result
    else:
        return []


def get_dict(cursor):
    fields = [d[0].lower() for d in cursor.description]
    rst = cursor.fetchone()
    if rst:
        result = dict(zip(fields, rst))
        return result
    else:
        return None


def dict2obj(dct, obj_tag):
    if dct is None:
        return None
    for key, value in dct.items():
        setattr(obj_tag, key, value)
    return obj_tag


def get_properties():
    try:
        # 打开文本文件
        file = open(file_dir('resource/application.properties'), 'r')
    
        # 遍历文本文件的每一行，strip可以移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
        for line in file.readlines():
            if not line.strip():
                continue
            line = line.strip()
            k = line.split('=')[0]
            v = line.split('=')[1]
            gl.set_value(k, v)
    
        # 依旧是关闭文件
        file.close()
    except Exception as error:
        print(error)


def add_param_sql(sql, params):
    exec_sql = sql
    if params is not None:
        for key, value in params.items():
            if isinstance(value, str):
                exec_sql = exec_sql.replace('#{' + key + '}', "'" + value + "'")
            elif isinstance(value, list):
                exec_sql = exec_sql.replace('#{' + key + '}', list_to_where(value))
            else:
                exec_sql = exec_sql.replace('#{' + key + '}', str(value))
    return exec_sql


def list_to_where(list):
    if not list:
        return ''
    if isinstance(list[0], int):
        return ','.join(list)

    s = str()
    for i in list:
        s = s + "'" + str(i) + "'" + ','
    s = s.rstrip(',')
    return s


@atexit.register
def close_connection():
    mysql_connection = gl.get_value('mysql_connection')
    oracle_connection = gl.get_value('oracle_connection')
    mysql_cursor = gl.get_value('mysql_cursor')
    oracle_cursor = gl.get_value('oracle_cursor')
    oracle_pool = gl.get_value('oracle_pool')
    mysql_pool = gl.get_value('mysql_pool')

    if mysql_connection is not None:
        mysql_connection.close()
    if oracle_connection is not None:
        oracle_connection.close()
     #   print('Close Oracle Connection success')
    if mysql_cursor is not None:
        mysql_cursor.close()
    if oracle_cursor is not None:
        oracle_cursor.close()
    if mysql_pool is not None:
        mysql_pool.close()
    if oracle_pool is not None:
        oracle_pool.close()


def get_from_database(sql, clazz=object, sub_clazz=DataBaseData, params=None, resource='oracle'):
    connection = get_connection(resource)
    exec_sql = add_param_sql(sql, params)
    cursor = connection.cursor()
    cursor.execute(exec_sql)
    if clazz == list:
        result = []
        if sub_clazz in (int, bool, str, float):
            for data in cursor.fetchall():
                result.append(sub_clazz(data[0]))
        elif sub_clazz == dict:
            result = get_dict_list(cursor)
        else:
            for data in get_dict_list(cursor):
                ob = sub_clazz()
                result.append(dict2obj(data, ob))
    elif clazz in (int, bool, str, float):
        result = cursor.fetchone()
        result = sub_clazz(result[0])
    elif clazz == dict:
        result = get_dict(cursor)
    else:
        ob = clazz()
        result = dict2obj(get_dict(cursor), ob)
    cursor.close()
    connection.close()
    return result


def get_connection(resource):
    if resource == 'oracle':
        key = 'oracle_pool'
    elif resource == 'mysql':
        key = 'mysql_pool'
    else:
        raise RuntimeError('Resource not has this resource %s' % resource)
    pool = gl.get_value(key)
    if pool is None :
        return None
    connection = pool.connection()
    return connection
