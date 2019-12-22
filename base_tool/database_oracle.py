import cx_Oracle
import os
from base_tool.database import *
from DBUtils.PooledDB import PooledDB

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

gl._init()


class DataBaseData:
    pass


def create_oracle_pool():
    get_properties()
    pool = gl.get_value('oracle_pool')
    if pool is None:
        pool = PooledDB(cx_Oracle, 3, 5,maxconnections=5,blocking=True, user=gl.get_value('oracle.database.username'),
                        password=gl.get_value('oracle.database.password'), dsn=(('%s/%s') % (gl.get_value('oracle.database.url'),gl.get_value('oracle.database.db'))))
        gl.set_value('oracle_pool', pool)
        print('Create Oracle Pool success')


def create_oracle_connection():
    get_properties()
    pool = gl.get_value('oracle_pool')
    if pool is None:
        connection = gl.get_value('oracle_connection')
        if connection is None:
            connection = cx_Oracle.connect(user=gl.get_value('oracle.database.username'),
                                           password=gl.get_value('oracle.database.password'),
                                           dsn=(('%s/%s') % (gl.get_value('oracle.database.url'),gl.get_value('oracle.database.db'))))
            gl.set_value('oracle_connection', connection)
        return connection
    else:
        return pool.connection()

def makeDictFactory(cursor):
    columnNames = [d[0].lower() for d in cursor.description]

    def createRow(*args):
        return dict(zip(columnNames, args))

    return createRow


def makeNamedTupleFactory(cursor):
    columnNames = [d[0].lower() for d in cursor.description]
    import collections
    Row = collections.namedtuple('Row', columnNames)
    return Row


def get_from_oracle(sql, clazz=object, sub_clazz=DataBaseData, params=None,use_pool=False):
    connection = create_oracle_connection()
    if connection is None:
        raise Exception('Not have connection')
    cursor = connection.cursor()
    exec_sql = add_param_sql(sql, params)

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
    if gl.get_value('oracle_pool') is not None:
        connection.close()
    return result
