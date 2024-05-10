from unittest.mock import patch

import pytest
import uuid
import db.db_ids


def uuid_gen():
    return uuid.UUID('1d0c3710-2ea6-4fec-9045-2d2a8ccdd790', version=4)


def test_generate_device_id():
    new_uuid = uuid.uuid4()
    def fixed_uuid():
        return new_uuid

    with patch.object(uuid, 'uuid4', fixed_uuid):
        assert db.db_ids.generate_device_id() == uuid.uuid4()


def test_generate_log_id():
    assert False


def test_get_tag_id():
    assert False


def test_generate_tag_id():
    assert False


def test_existing_tag_id():
    assert False


def test_snowflake_idgenerator():
    assert False
