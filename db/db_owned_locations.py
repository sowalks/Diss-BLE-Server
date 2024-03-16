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
'WHERE DevicePosition != Point(-200,-200) AND '
''
 'NOT EXISTS (SELECT LocationHistory.LogID FROM LocationHistory INNER JOIN Registration '
 'ON LocationHistory.TagID = Registration.TagID WHERE mode = 0) GROUP BY LOGID'




# find most recent valid (not (-200,-200))
# unblocked which does not have a log id that is masked by blocked
# i.e. there does not exist a blocked log id which is in unblocked logid +/- BLOCK_TIME_MS << 22

# logid of the tagid that is owned and blocked - if a tagid is not blocked we still need owned tags separetl

# Get unblocked owned tags
('SELECT Time, lh.LogID, lh.TagID, Distance, DevicePosition FROM '
 'LocationHistory lh INNER JOIN Registration r ON r.TagID = lh.TagID'
 'WHERE r.DeviceID = %s AND DevicePosition != Point(-200,-200) AND NOT EXISTS('
 'SELECT AllBlocked.LogID FROM AllBlocked WHERE AllBlocked.LogID = lh.LogID) ')


# Get Owned Blocked
('SELECT AllBlocked.LogID, AllBlocked.TagID FROM '
 'AllBlocked INNER JOIN Registration r ON r.TagID = lh.TagID'
 'WHERE r.DeviceID = %s AND DevicePosition != Point(-200,-200) AND NOT EXISTS('
 'SELECT AllBlocked.LogID FROM AllBlocked WHERE AllBlocked.LogID = lh.LogID) ')


('SELECT MAX(UB.LogID) Time, UB.TagID, Distance, ST_X(DevicePosition), ST_Y(DevicePosition) '
 'FROM AllBlocked INNER JOIN Registration r ON r.TagID = B.TagID '
 'RIGHT JOIN LocationHistory lh ON r.TagID = lh.TagID ' # right join to keep unblocked owned tags
 'WHERE r.DeviceID = %s AND DevicePosition != Point(-200,-200) AND' # get owned and valid unblocked locations (allblocked does not need valid loc)
 'AND AllBlocked.LogID is NULL AND ' #Removes Blocked LogIDs
 'NOT EXISTS (SELECT LogID FROM AllBlocked WHERE lh.LogID + %s <= AllBlocked.LogID OR lh.LogID - %s >=  AllBlocked.LogID )')


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

