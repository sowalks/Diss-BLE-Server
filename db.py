# db.py
from struct import pack, unpack

import pymysql
from connections import open_connection
import logging

log = logging.getLogger('database')


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
            log.info("device id generated: " + str(device_id))
            conn.commit()
        except pymysql.Error as e:
            log.error("Error Generating Device ID: " + str(e))
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
            log.error("tagid generated: " + str(tag_id))
        except pymysql.Error as e:
            log.error("Error Generating TagID: " + str(e))
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
            log.error("Error Getting Locations: " + str(e))
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
            log.error("Check tag exists: " + str(e))
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
                                    (update['mode'], update['tag_id'], update['device_id']))
            conn.commit()
            # result returns rows affected.
            # check if valid to same mode, or invalid ids
            if result == 0:
                cursor.execute('SELECT COUNT(*) FROM Registration WHERE TagID = %s AND DeviceID = %s',
                                         (update['tag_id'], update['device_id']))
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


def store_location_log(entry, blocked, tag_id):
    print(blocked)
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                'INSERT INTO LocationHistory (Time,TagID,Distance,DevicePosition,Blocked) VALUES(%s, %s, %s, '
                'Point(%s,%s), %s)',
                (entry["time"], tag_id, entry["distance"], entry["device_position"]["longitude"],
                 entry["device_position"]["latitude"], blocked))
            conn.commit()
            log.info("Log Stored")
        except pymysql.IntegrityError as i:
            # this is to let app know if there is a duplicate
            # if the log has already been stored
            if str(i).startswith('(1062,'):
                log.warning("Duplicate Location Log: " + str(i))
                if blocked:
                    return update_blocked_tag(entry['time'], tag_id, conn)
                return -2
            log.error("Error Logging: " + str(i))
            return -1
        except pymysql.Error as e:
            log.error("Error Logging: " + str(e))
            return -1
        finally:
            conn.close()
        return 0


def is_inhibited(tag_ids):
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            placeholders = '%s,' * (len(tag_ids) - 1) + '%s'
            cursor.execute(
                'SELECT COUNT(*) FROM Registration WHERE TagID IN (' + placeholders + ') AND MODE = 0',
                tuple(tag_ids))
            result = cursor.fetchone()[0]
        except pymysql.Error as e:
            log.error("Inhibit Error: " + str(e))
            return -1
        finally:
            conn.close()
        return 1 if result > 0 else result


def update_blocked_tag(time, tag_id, conn):
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                'UPDATE LocationHistory SET Blocked = 1 WHERE Time = %s AND TagID = %s',
                (time, tag_id))
            conn.commit()
            log.info("Log Stored")
        except pymysql.Error as e:
            log.error("Error Updating Duplicate: " + str(e))
            return -1
        return 0
