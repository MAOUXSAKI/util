import pymysql
from base_tool.database import *
from DBUtils.PooledDB import PooledDB


def create_mysql_connection():
    get_properties()
    pool = gl.get_value('mysql_pool')
    if pool is None:
        print('Create mysql Pool success')
        pool = PooledDB(pymysql, 10, 20,
                        host=gl.get_value('mysql.database.url'),
                        user=gl.get_value('mysql.database.username'),
                        passwd=gl.get_value('mysql.database.password'),
                        db=gl.get_value('mysql.database.db'),
                        port=3306,
                        charset='utf8mb4')
        gl.set_value('mysql_pool', pool)
    return pool.connection()


def get_from_mysql(sql, clazz=object, sub_clazz=object, params=None):
    connection = create_mysql_connection()
    exec_sql = add_param_sql(sql, params)
    cursor = connection.cursor()
    cursor.execute(exec_sql)
    if clazz == list:
        result = []
        if sub_clazz in (int, bool, str, float):
            for data in cursor.fetchall():
                result.append(data[0])
        elif sub_clazz == dict:
            result = get_dict_list(cursor)
        else:
            for data in get_dict_list(cursor):
                ob = sub_clazz()
                result.append(dict2obj(data, ob))
    elif clazz in (int, bool, str, float):
        result = cursor.fetchone()
        result = result[0]
    elif clazz == dict:
        result = get_dict(cursor)
    else:
        ob = clazz()
        result = dict2obj(get_dict(cursor), ob)
    cursor.close()
    connection.close()
    return result


def exec_to_mysql(sql, params=None):
    connection = create_mysql_connection()
    cursor = connection.cursor()
    exec_sql = add_param_sql(sql, params)
    cursor.execute(exec_sql)
    connection.commit()
    cursor.close()
