import pymysql
import logging
from db.connections import open_connection

log = logging.getLogger('db log')


def store_location_log(entry, log_id, tag_id):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO LocationHistory (TagID,Time,Distance,DevicePosition,LogID) VALUES(%s, %s, %s, '
                'Point(%s,%s), %s)', # returns bigint for logid
                (tag_id, entry["time"], entry["distance"], entry["device_position"]["longitude"],
                 entry["device_position"]["latitude"], log_id))
            conn.commit()
            log.info("Log Stored")
        except pymysql.IntegrityError as i:
            log.error("Error Logging: " + str(i))
            return -1
        except pymysql.Error as e:
            log.error("Error Logging: " + str(e))
            return -1
        finally:
            conn.close()
        return 0
