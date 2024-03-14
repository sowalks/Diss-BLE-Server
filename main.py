from db import store_location_log, register_tag, get_last_unblocked_locations, generate_device_id, set_mode, \
    get_tag_id, is_inhibited
from schema import LocationListSchema, RegistrationSchema, UpdateSchema
from flask import Flask, jsonify, request
from marshmallow import ValidationError

app = Flask(__name__)


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
        return jsonify({"msg": "Database Error for Locating Tags"}), 400
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
        return jsonify({"msg": str(err)}), 400

    tag_ids = [get_tag_id(entry['tag']) for entry in log['entries']]
    blocked = is_inhibited(tag_ids)
    if blocked == -1:
        return jsonify({"msg": "Error detecting inhibited"}), 400
    results = [store_location_log(entry, blocked, tag_id) for entry, tag_id in zip(log['entries'], tag_ids)]
    app.logger.info("Successful Log: length " + str(len(results)) + " Blocked : " + str(blocked))
    return jsonify(status=results)


@app.route('/registration', methods=['POST'])
# register a tag to a device, so it can be located by them
def register():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        try:
            r = RegistrationSchema().load(request.json)
        except ValidationError as err:
            return str(err), 400
        # return status error, already registered or tag_id
        return jsonify(status=register_tag(r))


@app.route('/device')
def get_device_id():
    # generate device id to be able to register & locate
    # tags. This is not the focus of the project, it is a placeholder
    # for a general secure login or identifying a device.
    device_id = generate_device_id()
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
