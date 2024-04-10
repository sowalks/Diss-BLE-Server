import uuid

import pymysql
from db.connections import open_connection
import logging


# +/- time to keep blocked in log format log
BLOCK_TIME = 30000 << 22
log = logging.getLogger('database')


def get_last_unblocked_locations(device_id):
    # selects only the most recent location of all tags the device owns
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute(  # AllBlocked is a view of all blocked tagid and logids
                'SELECT LocationHistory.Time, LocationHistory.TagID, LocationHistory.Distance, ST_X(LocationHistory.DevicePosition), ST_Y(LocationHistory.DevicePosition) '
                'FROM LocationHistory INNER JOIN '
                '(SELECT Max(LocationHistory.LogID) AS idlogs, LocationHistory.TagID AS idtags, LocationHistory.Time AS newtime ' #most recent log 
                'FROM locationhistory  INNER JOIN Registration ON Registration.TagID = LocationHistory.TagID WHERE'
                ' registration.DeviceID =  UUID_TO_BIN(%s) AND DevicePosition != Point(-200,-200)'
                ' AND LocationHistory.LogID NOT IN '
                '(SELECT AllBlocked.LogID from AllBlocked INNER JOIN LocationHistory'
                ' on  locationHistory.tagid = Allblocked.tagid'
                ' where AllBlocked.LogID = locationhistory.LogID  '
                'AND (LocationHistory.LogID + %s) >= AllBlocked.LogID '
                'AND (LocationHistory.LogID - %s) <=  AllBlocked.LogID)'
                '  GROUP BY LocationHistory.TagID, LocationHistory.Time ORDER BY Time Desc LIMIT 1) o ' # most recent time if multiple in logid
                'ON idtags =LocationHistory.TagID WHERE idlogs = LocationHistory.LogID;',
                (device_id, BLOCK_TIME, BLOCK_TIME))
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
