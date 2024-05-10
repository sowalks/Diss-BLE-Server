import logging
import pymysql

log = logging.Logger("Database Connection")


def open_connection():
    try:
        conn = pymysql.connect(host='127.0.0.1', user='sw', password='RoI&Q/TYyic7ru$', db='tag_tracking',
                               )
    except pymysql.MySQLError as e:
        log.error(e)
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
        log.error(e)
    '''
