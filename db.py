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
            cursor.execute('INSERT INTO Tag (UUID, Major, Minor) VALUES(%s, %s, %s)', (tag["UUID"], tag["Major"],
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
    # selects only the most recent location of all tags the device owns
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute(
                'SELECT  Time, TagID, Distance, ST_X(DevicePosition), ST_Y(DevicePosition) FROM LocationHistory WHERE '
                '(Time, TagID) in (SELECT  Max(LocationHistory.Time), LocationHistory.TagID FROM LocationHistory '
                'INNER JOIN Registration ON LocationHistory.TagID = Registration.TagID WHERE DeviceID = %s AND Blocked '
                '= 0 GROUP BY TagID);', (device_id,))
            recent = cursor.fetchall()
            if result > 0:
                locations = []
                for r in recent:
                    locations.append({"time": str(r[0]), "tag_id": r[1], "distance": r[2],
                                      "device_position": {"longitude": r[3], "latitude": r[4]}})
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
                tag_id = cursor.fetchone()[0]
            else:
                tag_id = None
        except pymysql.Error as e:
            print(e)
            tag_id = -1
        finally:
            conn.close()
    return tag_id


def register_tag(tag_id, device_id, tag_mode):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO Registration(TagID,DeviceID,Mode) VALUES(%s, %s, %s)',
                           (tag_id, device_id, tag_mode))
            conn.commit()
        except pymysql.IntegrityError as i:
            # this is to let app know if the error was a duplicate or
            # if it has been already registered.
            print(i)
            return str(i)
        except pymysql.Error as e:
            print(e)
            return -1
        finally:
            conn.close()
    return 0


def store_location_log(log):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO LocationHistory (Time,TagID,Distance,DevicePosition,Blocked) VALUES(%s, %s, %s, '
                'Point(%s,%s), 0)',
                (log["time"], log["tag_id"], log["distance"], log["device_position"]["longitude"],log["device_position"]["latitude"]))
            conn.commit()
        except pymysql.IntegrityError as i:
            # this is to let app know if there is a duplicate
            # if the log has already been stored
            print(i)
            return str(i)
        except pymysql.Error as e:
            print(e)
            return -1
        finally:
            conn.close()
        return 0