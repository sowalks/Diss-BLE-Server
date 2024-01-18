# main.py
import db
from flask import Flask, jsonify, request
from marshmallow import Schema, fields
app = Flask(__name__)


@app.route('/device')
def generate_devid_test():
    device_id = db.generate_device_id()
    return jsonify(device_id)


@app.route('/tag', methods=['POST'])
def generate_tagid_test():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.json
    tag_id = db.generate_tag_id(data.get('tag'))
    return jsonify(tag_id)


@app.route('/find', methods=['POST'])
def locate_tags_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        data = request.json
        db.get_last_unblocked_locations(data.get('device_id'))


@app.route('/tagid', methods=['POST'])
def tagid_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        data = request.json
        return db.get_tagid(data.get('tag'))


@app.route('/registration', methods=['POST'])
def registration_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        data = request.json
        return db.register_tag(data.get('tag_id', 'device_id'))


@app.route('/log', methods=['POST'])
def storelog_test():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        data = request.json
        return db.store_location_log(data.get('log'))


if __name__ == '__main__':
    app.run(debug=True)
