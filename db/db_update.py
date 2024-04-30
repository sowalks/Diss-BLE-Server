import pymysql
import logging
from db.connections import open_connection
from db.db_ids import get_tag_id

log = logging.getLogger('db update')


def register_tag(reg):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            tid = get_tag_id(reg['tag'])
            cursor.execute('INSERT INTO Registration(TagID,DeviceID,Mode) VALUES(%s, %s, %s)',
                           (tid, reg['device_id'].bytes, reg['mode']))
            conn.commit()
            log.info("Tag Registered - id:" + str(tid))
        except pymysql.IntegrityError as i:
            # this is to let app know if the error was a duplicate or
            # if it has been already registered.
            if str(i).startswith('(1062,'):
                log.warning("Duplicate Tag Registration: " + str(i))
                return -2
            log.error("Error Registering: " + str(i))
            return -1
        except pymysql.Error as e:
            log.error("Error Registering: " + str(e))
            return -1
        finally:
            conn.close()
    return tid


def set_mode(tag_id, update):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute('UPDATE Registration SET Mode = %s WHERE TagID = %s AND DeviceID = %s ',
                                    (update['mode'], tag_id, update['device_id'].bytes))
            conn.commit()
            # result returns rows affected.
            # check if valid to same mode, or invalid ids
            if result == 0:
                cursor.execute('SELECT COUNT(*) FROM Registration WHERE TagID = %s AND DeviceID = %s',
                               (tag_id, update['device_id'].bytes))
                not_valid = cursor.fetchone()[0]
                if not_valid == 0:
                    log.error("Incorrect IDs")
                    return -1
        except pymysql.Error as e:
            log.error("Set Mode Error: " + str(e))
            return -1
        finally:
            conn.close()
    return int(update['mode'])
