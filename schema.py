import datetime as dt
import struct

from marshmallow import Schema, fields, validate


class PositionSchema(Schema):
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)


class TagSchema(Schema):
    uuid = fields.UUID(required=True)
    # converts the unsigned shorts (H) into byte strings
    major = fields.Int(validate=validate.Range(0, 65535), required=True)
    minor = fields.Int(validate=validate.Range(0, 65535), required=True)


class LocationSchema(Schema):
    time = fields.DateTime(required=True)
    tag = fields.Nested(TagSchema(), required=True)
    tag_id = fields.Int(required=True)
    distance = fields.Float(required=True)
    device_position = fields.Nested(PositionSchema(), required=True)


class LocationListSchema(Schema):
    entries = fields.List(fields.Nested(LocationSchema()), required=True)


class RegistrationSchema(Schema):
    tag = fields.Nested(TagSchema(), required=True)
    device_id = fields.UUID(required=True)
    mode = fields.Bool(truthy={True}, falsy={False}, required=True)


class UpdateSchema(Schema):
    tag_id = fields.Int(required=True)
    device_id = fields.UUID(required=True)
    mode = fields.Bool(truthy={True}, falsy={False}, required=True)
