from db.db_ids import get_tag_id, generate_device_id, SnowflakeIDGenerator
from db.db_log import store_location_log
from db.db_owned_locations import get_last_unblocked_locations
from db.db_update import register_tag, set_mode
from schema import LocationListSchema, RegistrationSchema, UpdateSchema
from flask import Flask, jsonify, request
from marshmallow import ValidationError

app = Flask(__name__)
# individual for workers
id_gen = SnowflakeIDGenerator()


@app.route('/locations', methods=['POST'])
def find_recent_locations():
    # gets most recent unblocked location
    # of every tag registered to device
    # returns -1/error, message/no locations, results/all entries
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    result = get_last_unblocked_locations(request.json.get('device_id'))
    if result == -1:
        app.logger.error("locating error")
        return jsonify({"msg": "Database Error for Locating Tags"}), 500
    if result == 'No Recent Locations':
        app.logger.info(result)
        return jsonify({"entries": []})
    # return location list with tag_id not full tag fields
    return LocationListSchema(exclude=('entries.tag',)).dump({'entries': result})


@app.route('/log', methods=['POST'])
def store_log():
    # store log of location entries.
    # returns success/0, duplicate/-2, or error/-1,
    # so we know what was successful & what needs to be resent.
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    try:
        # load location with all tag fields
        log = LocationListSchema(exclude=('entries.tag_id',)).load(request.json)
    except ValidationError as err:
        app.logger.error("Store Log ValidationError:" + str(err))
        app.logger.error(str(request.json))
        return jsonify({"msg": str(err)}), 400
    log_id = id_gen.generate_log_id(log['entries'][0]['time'].timestamp())
    tag_ids = []
    entries = []
    #ensure only earliest entry for the same time in log is kepy
    for entry in log['entries']:
        tid = get_tag_id(entry['tag'])
        if not tid in tag_ids:
            tag_ids.append(tid)
            entries.append(entry)
    results = [store_location_log(entry, log_id, tag_id) for entry, tag_id in zip(entries, tag_ids)]
    app.logger.info("Successful Log: length " + str(len(results)))
    return jsonify(status=results)


@app.route('/registration', methods=['POST'])
# register a tag to a device, so it can be located by them
def register():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    try:
        r = RegistrationSchema().load(request.json)
    except ValidationError as err:
        return str(err), 400
    # return status error, already registered or tag_id
    return jsonify(status=register_tag(r))


@app.route('/device',methods=["POST"])
def get_device_id():
    # generate device id to be able to register & locate
    # tags. This is not the focus of the project, it is a placeholder
    # for a general secure login or identifying a device.
    device_id = generate_device_id()
    if device_id == -1:
        return jsonify({"msg": "Could not Generate DeviceID"}), 500
    return jsonify(device_id=device_id)


@app.route('/set-mode', methods=['PUT'])
def set_tag_mode():
    if request.method == 'PUT':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        try:
            update = UpdateSchema().load(request.json)
        except ValidationError as err:
            return str(err), 400
        # return status error or mode set /error(invalid uuids,server,etc)
        return jsonify(status=set_mode(update))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
