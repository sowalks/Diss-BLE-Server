# main.py
import db
from schema import LocationSchema, TagSchema, RegistrationSchema
from flask import Flask, jsonify, request
from marshmallow import ValidationError

app = Flask(__name__)


@app.route('/device')
def generate_devid_test():
    device_id = db.generate_device_id()
    return jsonify(device_id)


@app.route('/tag', methods=['POST'])
def generate_tagid_test():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    try:
        tag = TagSchema().load(request.json)
    except ValidationError as err:
        return str(err), 400
    tag_id = db.generate_tag_id(tag)
    return jsonify(tag_id=tag_id)


@app.route('/find', methods=['POST'])
def locate_tags_test():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    result = db.get_last_unblocked_locations(request.json.get('device_id'))
    if result == -1:
        return jsonify({"msg": "Database Error for Locating Tags"}), 400
    if result == 'No Recent Locations':
        return jsonify(result)
    print(result)
    return LocationSchema().load(data=result, many=True)


@app.route('/tagid', methods=['POST'])
def tagid_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        try:
            tag = TagSchema().load(request.json)
        except ValidationError as err:
            return str(err), 400
        return jsonify(tagid=db.get_tagid(tag))


@app.route('/registration', methods=['POST'])
def registration_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        try:
            r = RegistrationSchema().load(request.json)
        except ValidationError as err:
            return str(err), 400
        return jsonify(status=db.register_tag(r['tag_id'], r['device_id'], r['mode']))


@app.route('/log', methods=['POST'])
def store_log_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        try:
            log = LocationSchema().load(request.json)
        except ValidationError as err:
            return str(err), 400
        return jsonify(status=db.store_location_log(log))


if __name__ == '__main__':
    app.run(debug=True)
