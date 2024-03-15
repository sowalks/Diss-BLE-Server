import pymysql
from connections import open_connection
import logging

from db.db_ids import to_bytes, time_from_id
# +/- blocktime from log
BLOCK_TIME_MS = 30000
log = logging.getLogger('database')

# This method is better to be able to see who is inhibiting dynamically, rather than storing blocked/not, which is redundant
# get all most recent logid for each owned tag where position not invalid (-200,-200) & not in last BLOCK_TIME
# check if blocked: if blocked - skip BLOCK_TIME in ids, and find the next most recent until unblocked
# if not blocked - check if blocked in any surrounding time BLOCK if yes

# We want within time bounds from blocked list not unblocked list

'SELECT COUNT(*) FROM Registration WHERE TagID IN (' + placeholders + ') AND MODE = 0',

# its find all times tags are blocked ever then check most recent unblocked which is not close to them
# or its find all unblocked ever then check if tags are blocked near them, then find most recent which is not

# Get owned tags
'SELECT LocationHistory.TagID FROM LocationHistory '
                'INNER JOIN Registration ON LocationHistory.TagID = Registration.TagID WHERE DeviceID = %s GROUP BY TagID'

# for tag, Find all blocked log id

#find all blocked logs
'SELECT LocationHistory.LogID FROM LocationHistory'
'INNER JOIN Registration ON LocationHistory.TagID = Registration.TagID '
 'WHERE mode = 0 AND '
 'GROUP BY LocationHistory.LogID'

# select from
'SELECT Time, MAX(LogID), TagID, Distance, ST_X(DevicePosition), ST_Y(DevicePosition) FROM LocationHistory '
                'WHERE ST_X(DevicePosition)NOT EXISTS (SELECT 1 FROM LocationHistory INNER JOIN Registration ON LocationHistory.TagID = Registration.TagID '
 'WHERE mode = 0 AND LogID = logid ) AND'

# find most recent valid (not (-200,-200))
# unblocked which does not have a log id that is masked by blocked
# i.e. there does not exist a blocked log id which is in unblocked logid +/- BLOCK_TIME_MS << 22


def get_last_unblocked_locations(device_id):
    # selects only the most recent location of all tags the device owns
    conn = open_connection()
    with conn.cursor() as cursor:
        try:
            result = cursor.execute(
                'SELECT Time, LogID, TagID, Distance, ST_X(DevicePosition), ST_Y(DevicePosition) FROM LocationHistory '
                'WHERE'
                '(Time, TagID) in ();', (to_bytes(device_id),))
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

