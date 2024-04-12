import datetime
import secrets

import pymysql
import logging
import uuid
from struct import pack

from db.connections import open_connection

log = logging.getLogger('db ids')


class SnowflakeIDGenerator:
    def __init__(self):
        # generate every run/ clear to see in db when each session is
        self.machine = secrets.randbits(10)
        self.seq = 0
        self.last_timestamp = 0

    # based on SnowflakeID, with random as machine and sequence number
    # ensures concise timestamp + log grouping without deviceID
    # can be made scalable by transferring to full snowflake
    def generate_log_id(self, timestamp):
        ts = int(timestamp * 1000)
        # keep ordering for seq so no duplicates
        if ts == self.last_timestamp or ts < self.last_timestamp:
            self.seq += 1
        else:
            self.last_timestamp = ts
            self.seq = 0
        return self.last_timestamp << 22 | self.machine << 12 | self.seq


def generate_device_id():
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            device_id = uuid.uuid4()
            cursor.execute('INSERT INTO Device (DeviceID) VALUES (%s);', (device_id.bytes,))
            conn.commit()
        except pymysql.Error as e:
            log.error("Error Generating Device ID: " + str(e))
            # if db fails we can try again based on device id
            device_id = -1
        finally:
            conn.close()
    return device_id


def get_tag_id(tag):
    tid = existing_tag_id(tag)
    if tid is None:
        tid = generate_tag_id(tag)
    return tid


def generate_tag_id(tag):
    # same reasoning as register device
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO Tag (UUID, Major, Minor) VALUES(%s, %s, %s)',
                           (tag["uuid"].bytes,
                            tag["major"].to_bytes(2),
                            tag["minor"].to_bytes(2)))
            conn.commit()
            tag_id = cursor.lastrowid
            log.error("tagid generated: " + str(tag_id))
        except pymysql.Error as e:
            log.error("Error Generating TagID: " + str(e))
            tag_id = -1
        finally:
            conn.close()
    return tag_id


def existing_tag_id(tag):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute('SELECT TagID FROM Tag WHERE UUID = %s AND Major = %s  AND Minor = %s ;',
                                    (tag['uuid'].bytes, tag["major"].to_bytes(2),
                                    tag["minor"].to_bytes(2)))
            if result > 0:
                tag_id = cursor.fetchone()[0]
            else:
                tag_id = None
        except pymysql.Error as e:
            log.error("Check tag exists: " + str(e))
            tag_id = -1
        finally:
            conn.close()
    return tag_id



