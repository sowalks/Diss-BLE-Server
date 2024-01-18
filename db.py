# db.py
import os
import pymysql
from flask import jsonify
from connections import open_connection



def generate_device_id():
    device_id = None
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO Device (DeviceID) VALUES (0);')
            # lastrowid is safe to use,no race condtiions because I am not
            # sharing a connection object
            device_id = cursor.lastrowid
            conn.commit()
        except pymysql.Error as e:
            print(e)
            # if db fails we can try again based on device id
            device_id = -1
        finally:
            conn.close()
    return device_id


def generate_tag_id(tag):
    # same reasoning as register device
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO Tag (UUID, Major, Minor) VALUES(%s, %s, %s)', (tag['UUID'], tag["Major"],
                                                                                       tag["Minor"]))
            tag_id = cursor.lastrowid
            conn.commit()
        except pymysql.Error as e:
            print(e)
            tag_id = -1
        finally:
            conn.close()
    return tag_id

def get_last_unblocked_locations(device_id):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute('SELECT LocationHistory.TagID, DevicePosition, Distance FROM LocationHistory '
                                    'INNER JOIN Registration ON LocationHistory.TagID = Registration.TagID WHERE '
                                    'DeviceID = %s AND Blocked = 0 ORDER BY Time DESC LIMIT 1;', (device_id,))
            recent = cursor.fetchall()
            if result > 0:
                locations = recent
            else:
                locations = 'No Recent Locations'
        except pymysql.Error as e:
            print(e)
            locations = -1
        finally:
            conn.close()
    return locations


def get_tagid(tag):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute('SELECT TagID FROM Tag WHERE UUID = %s AND Major = %s  AND Minor = %s ;',
                                    (tag['UUID'], tag["Major"], tag["Minor"]))
            if result > 0:
                tag_id = cursor.fetchall()
            else:
                tag_id = None
        except pymysql.Error as e:
            print(e)
        finally:
            conn.close()
    return tag_id
def register_tag(tag_id, device_id, tag_mode):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO Registration(Tag_ID,Device_ID,Mode) VALUES(%s, %s, %s)',
                           (tag_id, device_id, tag_mode))
            conn.commit()
        except pymysql.Error as e:
            print(e)
        finally:
            conn.close()
    return

def store_location_log(log):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO LocationHistory (Time,TagID,Distance,DevicePosition,Blocked) VALUES(%s, %s, %s, '
                '%s, %s)',
                (log["Time"], log["TagID"], log["Distance"], log["DevicePosition"], log["Blocked"]))
        except pymysql.Error as e:
            print(e)
        finally:
            conn.close()