import datetime as dt
from marshmallow import Schema, fields


class PositionSchema(Schema):
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)


class TagSchema(Schema):
    uuid = fields.Int(required=True)
    major = fields.Int(required=True)
    minor = fields.Int(required=True)


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
    device_id = fields.Int(required=True)
    mode = fields.Bool(truthy={True}, falsy={False}, required=True)
