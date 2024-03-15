import pymysql
import logging
from connections import open_connection
from db.db_ids import get_tag_id, to_bytes

log = logging.getLogger('db update')


def register_tag(reg):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            tid = get_tag_id(reg['tag'])
            cursor.execute('INSERT INTO Registration(TagID,DeviceID,Mode) VALUES(%s, %s, %s)',
                           (tid, to_bytes(reg['device_id']), reg['mode']))
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


def set_mode(update):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute('UPDATE Registration SET Mode = %s WHERE TagID = %s AND DeviceID = %s ',
                                    (update['mode'], update['tag_id'], to_bytes(update['device_id'])))
            conn.commit()
            # result returns rows affected.
            # check if valid to same mode, or invalid ids
            if result == 0:
                cursor.execute('SELECT COUNT(*) FROM Registration WHERE TagID = %s AND DeviceID = %s',
                               (update['tag_id'], to_bytes(update['device_id'])))
                not_valid = cursor.fetchone()[0]
                if not_valid == 0:
                    log.error("Incorrect IDs")
                    return -1
                log.info("Duplicate Set Mode")
        except pymysql.Error as e:
            log.error("Set Mode Error: " + str(e))
            return -1
        finally:
            conn.close()
    return int(update['mode'])
