

from db.db_ids import get_tag_id, generate_device_id, SnowflakeIDGenerator
from db.db_log import store_location_log
from db.db_owned_locations import get_last_unblocked_locations
from db.db_update import register_tag, set_mode
from schema import LocationListSchema, RegistrationSchema, UpdateSchema, DeviceIDSchema
from flask import Flask, jsonify, request
from marshmallow import ValidationError
from datetime import datetime


app = Flask(__name__)
# individual for workers
id_gen = SnowflakeIDGenerator()


@app.route('/locations/<device_id_str>', methods=['GET'])
def find_recent_locations(device_id_str):
    # gets most recent unblocked location
    # of every tag registered to device
    # returns -1/error, message/no locations, results/all entries
    try:
        device_id = DeviceIDSchema().load({"id": device_id_str})['id']
    except ValidationError:
        return jsonify({"msg": "Device Validation Error"}), 400
    result = get_last_unblocked_locations(device_id)
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
        return jsonify({"msg": "Store Log ValidationError"}), 400
    log_id = id_gen.generate_log_id(datetime.now().timestamp())
    tag_ids = dict()
    entries = []
    # ensure only latest entry for in one log is kept
    for entry in log['entries']:
        tid = get_tag_id(entry['tag'])
        if not str(tid) in tag_ids:
            tag_ids[str(tid)] = 0
            entries.append(entry)
        tag_ids[str(tid)] += 1
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
        return jsonify({"msg":"Invalid JSON"}), 400
    # return status error, already registered or tag_id
    return jsonify(status=register_tag(r))


@app.route('/device', methods=["POST"])
def gen_device_id():
    # generate device id to be able to register & locate
    # tags. This is not the focus of the project, it is a placeholder
    # for a general secure login or identifying a device.
    device_id = generate_device_id()
    if device_id <= 0:
        return jsonify({"msg": "Could not Generate DeviceID"}), 500
    return jsonify(device_id=device_id)


@app.route('/mode/<tag_id>', methods=['PUT'])
def set_tag_mode(tag_id=0):
    if request.method == 'PUT':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        try:
            update = UpdateSchema().load(request.json)
        except ValidationError as err:
            return jsonify({"msg":"Invalid JSON"}), 400
        # return status error or mode set /error(invalid uuids,server,etc)
        return jsonify(status=set_mode(tag_id, update))


if __name__ == '__main__':
        app.run(debug=False, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
