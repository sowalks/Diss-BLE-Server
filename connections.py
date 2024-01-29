import os
import pymysql

db_user = os.environ.get('MYSQL_USERNAME')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE_NAME')
db_connection_name = os.environ.get('MYSQL_CONNECTION_NAME')

def open_connection():
    try:
        conn = pymysql.connect(host='127.0.0.1', user='sw', password='RoI&Q/TYyic7ru$', db='tag_tracking',
                               )
    except pymysql.MySQLError as e:
        print(e)
    return conn

''' 
PRODUCTION OPEN CONNECTION:
unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user, password=db_password,
                                   unix_socket=unix_socket, db=db_name,
                                   cursorclass=pymysql.cursors.DictCursor
                                   )
    except pymysql.MySQLError as e:
        print(e)
    '''