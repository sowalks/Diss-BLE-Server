# db.py
from struct import pack, unpack

import pymysql
from connections import open_connection


def get_tag_id(tag):
    tid = existing_tag_id(tag)
    if tid is None:
        tid = generate_tag_id(tag)
    return tid


def to_bytes(field):
    return pack('H', field)


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
            cursor.execute('INSERT INTO Tag (UUID, Major, Minor) VALUES(%s, %s, %s)',
                           (tag["uuid"].bytes,
                            to_bytes(tag["major"]),
                            to_bytes(tag["minor"])))
            conn.commit()
            tag_id = cursor.lastrowid

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
                    locations.append({"time": r[0], "tag_id": r[1], "distance": r[2],
                                      "device_position": {"longitude": r[3], "latitude": r[4]}})

            else:
                locations = 'No Recent Locations'

        except pymysql.Error as e:
            print(e)
            locations = -1
        finally:
            conn.close()
    return locations


def existing_tag_id(tag):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute('SELECT TagID FROM Tag WHERE UUID = %s AND Major = %s  AND Minor = %s ;',
                                    (tag['uuid'].bytes, to_bytes(tag["major"]),
                                     to_bytes(tag["minor"])))
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


def register_tag(reg):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            tid = get_tag_id(reg['tag'])
            cursor.execute('INSERT INTO Registration(TagID,DeviceID,Mode) VALUES(%s, %s, %s)',
                           (tid, reg['device_id'], reg['mode']))
            conn.commit()
        except pymysql.IntegrityError as i:
            # this is to let app know if the error was a duplicate or
            # if it has been already registered.
            if str(i).startswith('(1062,'):
                print(i)
                return -2
            print(i)
            return -1
        except pymysql.Error as e:
            print(e)
            return -1
        finally:
            conn.close()
    return tid


def store_location_log(entry):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO LocationHistory (Time,TagID,Distance,DevicePosition,Blocked) VALUES(%s, %s, %s, '
                'Point(%s,%s), 0)',
                (entry["time"], get_tag_id(entry['tag']), entry["distance"], entry["device_position"]["longitude"],
                 entry["device_position"]["latitude"]))
            conn.commit()
        except pymysql.IntegrityError as i:
            # this is to let app know if there is a duplicate
            # if the log has already been stored
            if str(i).startswith('(1062,'):
                return -2

            print(i)
            return -1
        except pymysql.Error as e:
            print(e)
            return -1
        finally:
            conn.close()
        return 0
