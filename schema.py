import datetime as dt
from marshmallow import Schema, fields


class PositionSchema(Schema):
    longitude = fields.Float()
    latitude = fields.Float()


class LocationSchema(Schema):
    time = fields.DateTime()
    tag_id = fields.Int()
    distance = fields.Float()
    device_position = fields.Nested(PositionSchema())


class TagSchema(Schema):
    UUID = fields.Int()
    Major = fields.Int()
    Minor = fields.Int()


class RegistrationSchema(Schema):
    tag_id = fields.Int()
    device_id = fields.Int()
    mode = fields.Bool(truthy={True}, falsy={False})

