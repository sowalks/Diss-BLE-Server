
import uuid
from datetime import datetime
from unittest.mock import patch


import pytest
import main


@pytest.fixture
def client():
    # app created for testing
    client = main.app.test_client()
    yield client


## RECENT LOCATIONS


@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                      'ffffffff-ffff-ffff-ffff-ffffffffffff'])
def test_find_recent_locations_error(client, deviceid):
    def mock_locations(l):
        return -1

    with patch.object(main, 'get_last_unblocked_locations', mock_locations):
        response = client.get(f"/locations/{deviceid}")
        assert response.status_code == 500
        assert response.json["msg"] == "Database Error for Locating Tags"


@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                      'ffffffff-ffff-ffff-ffff-ffffffffffff'])
def test_find_recent_locations_empty_success(client, deviceid):
    def mock_locations(l):
        return []

    with patch.object(main, 'get_last_unblocked_locations', mock_locations):
        response = client.get(f"/locations/{deviceid}")
        assert response.status_code == 200
        assert response.json["entries"] == []



@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                      'ffffffff-ffff-ffff-ffff-ffffffffffff'])
def test_find_recent_locations_success(client, deviceid):
    def mock_locations(l):
        return [{"device_position": {"longitude": 0.13, "latitude": 52.2},  "distance": 0.2, "tag_id": 4,
                 "time": datetime.strptime('2024/04/16T21:51:01','%Y/%m/%dT%H:%M:%S')
                 }]

    with patch.object(main, 'get_last_unblocked_locations', mock_locations):
        response = client.get(f"/locations/{deviceid}")
        assert response.status_code == 200
        assert response.json["entries"] == [{'device_position': {'latitude': 52.2, 'longitude': 0.13}, 'distance': 0.2, 'tag_id': 4, 'time': '2024-04-16T21:51:01'}]



@pytest.mark.parametrize('deviceid',
                         ['56ae7e1f-0200-4128-ac03-3fae71af524g', '', '56ae7e1f-0t00-4128-ac03-3fae71af5245', 1,
                          '00000000-0000-0000-0000-000000', 'fffff'])
def test_find_recent_locations_validation_error(client,deviceid):
    def mock_locations(l):
        return []

    with patch.object(main, 'get_last_unblocked_locations', mock_locations):
        response = client.get(f"/locations/{deviceid}")
        assert response.status_code == 400
        assert response.json["msg"] == "Device Validation Error"


## STORE LOG
@pytest.mark.parametrize('data', [{"entries": [{"time": "2024-04-16T21:51:01.127", "tag": {"major": 59225, "minor": 12,
                                                                                           "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                "distance": 0.02690903368484794,
                                                "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                               {"time": "2024-04-16T21:51:01.127", "tag": {"major": 59225, "minor": 12,
                                                                                           "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                "distance": -1,
                                                "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                               {"time": "2024-04-16T21:51:01.127", "tag": {"major": 59225, "minor": 12,
                                                                                           "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                "distance": 0.02690903368484794,
                                                "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                               {"time": "2024-04-16T21:51:32.122", "tag": {"major": 59225, "minor": 10,
                                                                                           "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                "distance": 0.02690903368484794,
                                                "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                               {"time": "2024-04-16T21:51:20.122", "tag": {"major": 59225, "minor": 10,
                                                                                           "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                "distance": 0.02690903368484794,
                                                "device_position": {"longitude": 0.1173872, "latitude": 52.202838}}
                                               ]}, {"entries": [{"time": "2024-04-16T21:51:01.127",
                                                                 "tag": {"major": 59225, "minor": 12,
                                                                         "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                 "distance": 0.02690903368484794,
                                                                 "device_position": {"longitude": 0.1173872,
                                                                                     "latitude": 52.202838}},
                                                                {"time": "2024-04-16T21:51:01.127",
                                                                 "tag": {"major": 59225, "minor": 12,
                                                                         "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                 "distance": 0.02690903368484794,
                                                                 "device_position": {"longitude": 0.1173872,
                                                                                     "latitude": 52.202838}},
                                                                {"time": "2024-04-16T21:51:01.127",
                                                                 "tag": {"major": 59225, "minor": 12,
                                                                         "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                 "distance": 0.02690903368484794,
                                                                 "device_position": {"longitude": 0.1173872,
                                                                                     "latitude": 52.202838}},
                                                                {"time": "2024-04-16T21:51:32.122",
                                                                 "tag": {"major": -1, "minor": -1,
                                                                         "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                 "distance": 0.02690903368484794,
                                                                 "device_position": {"longitude": 0.1173872,
                                                                                     "latitude": 52.202838}},
                                                                {"time": "2024-04-16T21:51:20.122",
                                                                 "tag": {"major": 59225, "minor": 10,
                                                                         "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                 "distance": 0.02690903368484794,
                                                                 "device_position": {"longitude": 0.1173872,
                                                                                     "latitude": 52.202838}}
                                                                ]}, {"entries": [{"time": "2024-04-16T21:51:01.127",
                                                                                  "tag": {"major": 59225, "minor": 12,
                                                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                                  "distance": 0.02690903368484794,
                                                                                  "device_position": {
                                                                                      "longitude": 0.1173872,
                                                                                      "latitude": 52.202838}},
                                                                                 {"time": "2024-04-16T21",
                                                                                  "tag": {"major": 59225, "minor": 12,
                                                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                                  "distance": 0.02690903368484794,
                                                                                  "device_position": {
                                                                                      "longitude": 0.1173872,
                                                                                      "latitude": 52.202838}},
                                                                                 {"time": "2024-04-16T21:51:01.127",
                                                                                  "tag": {"major": 65336, "minor": 12,
                                                                                          "uuid": "777777fge-6b6b-6d63-6e2e-636f6d000001"},
                                                                                  "distance": 0.02690903368484794,
                                                                                  "device_position": {
                                                                                      "longitude": 0.1173872,
                                                                                      "latitude": 52.202838}},
                                                                                 {"time": "2024-04-16T21:51:32.122",
                                                                                  "tag": {"major": 59225, "minor": 10,
                                                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                                  "distance": 0.02690903368484794,
                                                                                  "device_position": {
                                                                                      "longitude": 0.1173872,
                                                                                      "latitude": 52.202838}},
                                                                                 {"time": "2024-04-16T21:51:20.122",
                                                                                  "tag": {"major": 59225, "minor": -1,
                                                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                                                  "distance": 0.02690903368484794,
                                                                                  "device_position": {
                                                                                      "longitude": 0.1173872,
                                                                                      "latitude": 52.202838}}
                                                                                 ]}, {"entries": [
    {"time": "2024-04-16T21:51:01.127",
     "tag": {"major": 59225, "minor": 12, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
     "distance": 0.02690903368484794, "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
    {"time": "2024-04-16T21:51:01.127",
     "tag": {"major": 59225, "minor": 12, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
     "distance": 0.02690903368484794, "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
    {"time": "2024-04-16T21:51:01.127",
     "tag": {"major": 59225, "minor": 12, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
     "distance": 0.02690903368484794, "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
    {"time": "2024-04-16T21:51:32.122",
     "tag": {"major": 59225, "minor": 10, "uuid": "7777772e-6fb6b-6d63-6e2e-636f6d000001"},
     "distance": 0.02690903368484794, "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
    {"time": "2024-04-16T21:51:20.122",
     "tag": {"major": 59225, "minor": 10, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
     "distance": 0.02690903368484794, "device_position": {"longitude": 0.1173872, "latitude": 52.202838}}
    ]}, {"entries": [{"time": "2024-04-16T21:51:01.127",
                      "tag": {"major": 59225, "minor": 12, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                      "distance": 0.02690903368484794,
                      "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                     {"time": "2024-04-16T21:51:01.127",
                      "tag": {"major": 59225, "minor": 12, "uuid": "7777772e-6bd6b-6d63-6e2e-636f6d000001"},
                      "distance": 0.02690903368484794,
                      "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                     {"time": "2024-04-16T21:51:01.127",
                      "tag": {"major": 59225, "minor": 12, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                      "distance": 0.02690903368484794,
                      "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                     {"time": "2024-04-16T21:51:32.122",
                      "tag": {"major": 59225, "minor": 10, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                      "distance": 0.02690903368484794,
                      "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                     {"time": "2024-04-16T21:51:20.122",
                      "tag": {"major": 59225, "minor": 10, "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                      "distance": 0.02690903368484794,
                      "device_position": {"longitude": 0.1173872, "latitude": 52.202838}}
                     ]}])
def test_store_log_validation_error(client, data):
    def mock_log(a, b, c):
        return 0

    with patch.object(main, 'store_location_log', mock_log):
        response = client.post("/log",
                               json=data)
        assert response.status_code == 400
        assert response.json["msg"] == "Store Log ValidationError"


@pytest.mark.parametrize('log_success', [0, -1])
def test_store_log_success_repeated_tag(client, log_success):
    def mock_log(a, b, c):
        return log_success

    with patch.object(main, 'store_location_log', mock_log):
        response = client.post("/log",
                               json={"entries": [{"time": "2024-04-16T21:51:01.127",
                                                  "tag": {"major": 59225, "minor": 12,
                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                  "distance": 0.02690903368484794,
                                                  "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                                 {"time": "2024-04-16T21:51:01.127",
                                                  "tag": {"major": 59225, "minor": 12,
                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                  "distance": 0.02690903368484794,
                                                  "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                                 {"time": "2024-04-16T21:51:01.127",
                                                  "tag": {"major": 59225, "minor": 12,
                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                  "distance": 0.02690903368484794,
                                                  "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                                 {"time": "2024-04-16T21:51:32.122",
                                                  "tag": {"major": 59225, "minor": 10,
                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                  "distance": 0.02690903368484794,
                                                  "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                                 {"time": "2024-04-16T21:51:20.122",
                                                  "tag": {"major": 59225, "minor": 10,
                                                          "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                                  "distance": 0.02690903368484794,
                                                  "device_position": {"longitude": 0.1173872, "latitude": 52.202838}}
                                                 ]})
        assert response.status_code == 200
        assert response.json["status"] == [log_success, log_success]


def test_store_log_success_unique_tags(client):
    def mock_log(a, b, c):
        return 0

    with patch.object(main, 'store_location_log', mock_log):
        response = client.post("/log",
                               json={"entries": [
                                   {"time": "2024-04-16T21:51:01.127", "tag": {"major": 59225, "minor": 12,
                                                                               "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                    "distance": 0.02690903368484794,
                                    "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                   {"time": "2024-04-16T21:51:32.122", "tag": {"major": 59225, "minor": 10,
                                                                               "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                    "distance": 0.02690903368484794,
                                    "device_position": {"longitude": 0.1173872, "latitude": 52.202838}},
                                   {"time": "2024-04-16T21:51:20.122", "tag": {"major": 59243, "minor": 12,
                                                                               "uuid": "7777772e-6b6b-6d63-6e2e-636f6d000001"},
                                    "distance": 0.02690903368484794,
                                    "device_position": {"longitude": 0.1173872, "latitude": 52.202838}}
                               ]})
        assert response.status_code == 200
        assert response.json["status"] == [0, 0, 0]


## REGISTER
@pytest.mark.parametrize('major', [65535, 12, 0])
@pytest.mark.parametrize('minor', [65535, 12, 0])
@pytest.mark.parametrize('mode', [0, 1])
@pytest.mark.parametrize('uuid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                  'ffffffff-ffff-ffff-ffff-ffffffffffff'])
@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                      'ffffffff-ffff-ffff-ffff-ffffffffffff'])
def test_register_success(client, mode, major, minor, uuid, deviceid):
    def mock_register(r):
        return 45

    with patch.object(main, 'register_tag', mock_register):
        response = client.post("/registration",
                               json={'tag': {'major': major, 'minor': minor, 'uuid': uuid}, 'device_id': deviceid,
                                     'mode': mode})
        assert response.status_code == 200
        assert response.json["status"] == 45


@pytest.mark.parametrize('major', [65535, 12, 0])
@pytest.mark.parametrize('minor', [65535, 12, 0])
@pytest.mark.parametrize('mode', [0, 1])
@pytest.mark.parametrize('uuid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                  'ffffffff-ffff-ffff-ffff-ffffffffffff'])
@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000',
                                      'ffffffff-ffff-ffff-ffff-ffffffffffff'])
def test_register_failure(client, mode, major, minor, uuid, deviceid):
    def mock_register(r):
        return -1

    with patch.object(main, 'register_tag', mock_register):
        response = client.post("/registration",
                               json={'tag': {'major': major, 'minor': minor, 'uuid': uuid}, 'device_id': deviceid,
                                     'mode': mode})
        assert response.status_code == 200
        assert response.json["status"] == -1


@pytest.mark.parametrize('major', [65536, -1, 12])
@pytest.mark.parametrize('minor', [65536, -1, 12])
@pytest.mark.parametrize('mode', [0, -1, 2])
@pytest.mark.parametrize('uuid',
                         ['56ae7e1f-0200-4128-ac03-3fae71af5245', 1, -1, '00000000-0000-0000-0000-000000', 'fffff'])
@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af524g', '56ae7e1f-0200-4128-ac03-3fae71af5245', 1,
                                      '00000000-0000-0000-0000-000000', 'fffff'])
def test_register_validation_error(client, mode, major, minor, uuid, deviceid):
    # Kept one valid combination to ensure even if only one field is incorrect, it does not validate
    if mode == 0 and minor == 12 and major == 12 and uuid == '56ae7e1f-0200-4128-ac03-3fae71af5245' and deviceid == '56ae7e1f-0200-4128-ac03-3fae71af5245':
        return

    def mock_register(r):
        return -1

    with patch.object(main, 'register_tag', mock_register):
        response = client.post("/registration",
                               json={'tag': {'major': major, 'minor': minor, 'uuid': uuid}, 'device_id': deviceid,
                                     'mode': mode})
        assert response.status_code == 400
        assert response.json['msg'] == "Invalid JSON"


## DEVICE ID GENERATE
def test_gen_device_id_get_failure(client):
    response = client.get("/device")
    assert response.status_code == 405


def test_gen_device_id_db_success(client):
    fixed_uuid = uuid.uuid4().int

    def new_uuid():
        return fixed_uuid

    with patch.object(main, 'generate_device_id', new_uuid):
        response = client.post("/device")
        assert response.status_code == 200
        assert response.json["device_id"] == fixed_uuid


@pytest.mark.parametrize("error_value", [-1, -100])
def test_gen_device_id_db_error(client, error_value):
    def error():
        return error_value

    with patch.object(main, 'generate_device_id', error):
        response = client.post("/device")
        assert response.status_code == 500
        assert response.json["msg"] == "Could not Generate DeviceID"


##SET MODE


@pytest.mark.parametrize('tagid', [400, 5, 2, 1, -1])
@pytest.mark.parametrize('mode', [True, False, 1, 0])
@pytest.mark.parametrize('deviceid',
                         ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000'])
def test_set_tag_mode_success(client, mode, tagid, deviceid):
    def mock_set_mode(tag, update):
        return mode

    with patch.object(main, 'set_mode', mock_set_mode):
        response = client.put(f"/mode/{tagid}", json={'device_id': deviceid, 'mode': mode})
        assert response.status_code == 200
        assert response.json["status"] == mode


@pytest.mark.parametrize('tagid', [400, 5, 2, 1, -1])
@pytest.mark.parametrize('mode', [True, False, 1, 0])
@pytest.mark.parametrize('deviceid', ['56ae7e1f-0200-4128-ac03-3fae71af5245', '00000000-0000-0000-0000-000000000000'])
def test_set_tag_mode_error(client, mode, tagid, deviceid):
    def mock_set_mode(tag, update):
        return -1

    with patch.object(main, 'set_mode', mock_set_mode):
        response = client.put(f"/mode/{tagid}", json={'device_id': deviceid, 'mode': mode})
        assert response.status_code == 200
        assert response.json["status"] == -1


@pytest.mark.parametrize('tagid', [400, -1, 2, 5])
@pytest.mark.parametrize('data', [{'device_id': '56ae7e1f-0200-4128-ac03-3fae71af5245', 'mode': 554},
                                  {'device_id': -56, 'mode': True},
                                  {'device_id': '56ae7e1f-0200-4128-ac03-3fae71af5245', 'mode': 'true'}])
def test_set_tag_mode_validation_error(client, tagid, data):
    def mock_set_mode(tagid, update):
        return 1

    with patch.object(main, 'set_mode', mock_set_mode):
        response = client.put(f"/mode/{tagid}", json=data)
        assert response.status_code == 400
        assert response.json['msg'] == "Invalid JSON"


@pytest.mark.parametrize('tagid', [400, 1, 5, -1])
def test_set_tag_mode_no_json_error(client, tagid):
    response = client.put(f"/mode/{tagid}")
    assert response.status_code == 400
    assert response.json['msg'] == "Missing JSON in request"

# Integration testing completed in Postman tool
