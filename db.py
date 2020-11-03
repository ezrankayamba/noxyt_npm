import mysql.connector
from mysql.connector import Error
import configparser
from contextlib import contextmanager


@contextmanager
def db_connect(*args, **kwargs):
    connection = None
    try:
        config = configparser.ConfigParser()
        config.read('my.cnf')
        client = dict(config['client'])
        # print(client)
        print('DB Connected!')
        connection = mysql.connector.connect(**client)
        # cursor = connection.cursor()
        yield connection
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection and connection.is_connected():
            # cursor.close()
            connection.close()
            print("MySQL connection is closed")
