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
                'SELECT Time, o.TagID, Distance, ST_X(DevicePosition), ST_Y(DevicePosition) FROM '
                'LocationHistory INNER JOIN '  # outer request for non aggregated fields when finding most recent
                '(SELECT MAX(lh.LogID) AS LogID, lh.TagID FROM '  # find most recent logid for owned tagid
                'LocationHistory lh INNER JOIN Registration r ON r.TagID = lh.TagID'  # check registration for ownership
                ' WHERE r.DeviceID = %s AND DevicePosition != Point(-200,-200) AND '  # position needs to be valid 
                'NOT EXISTS (SELECT LogID FROM AllBlocked b WHERE lh.TagID = b.TagID '  # check tag is not blocked in
                'AND (lh.LogID + %s) >= b.LogID AND (lh.LogID - %s <=  b.LogID)) '  # time range 
                'GROUP BY lh.TagID) o ON o.TagID=LocationHistory.TagID WHERE o.LogID = LocationHistory.LogID; ',
                (uuid.UUID(device_id).bytes, BLOCK_TIME, BLOCK_TIME))
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
