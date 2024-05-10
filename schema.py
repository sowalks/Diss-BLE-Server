from marshmallow import Schema, fields, validate, ValidationError, validates



def lat_range(value):
    if value != -200 and (value < -90 or value > 90):
        raise ValidationError("Must be valid latitude.")

def long_range(value):
    if value != -200 and (value < -180 or value > 180):
        raise ValidationError("Must be valid latitude.")

class PositionSchema(Schema):
    longitude = fields.Float(required=True, validate=long_range)
    latitude = fields.Float(required=True, validate=lat_range)


class TagSchema(Schema):
    uuid = fields.UUID(required=True)
    # converts the unsigned shorts (H) into byte strings
    major = fields.Int(validate=validate.Range(0, 65535), required=True)
    minor = fields.Int(validate=validate.Range(0, 65535), required=True)


class LocationSchema(Schema):
    time = fields.DateTime(required=True)
    tag = fields.Nested(TagSchema(), required=True)
    tag_id = fields.Int(required=True)
    distance = fields.Float(required=True, validate=validate.Range(0, ))
    device_position = fields.Nested(PositionSchema(), required=True)


class LocationListSchema(Schema):
    entries = fields.List(fields.Nested(LocationSchema()), required=True)


class DeviceIDSchema(Schema):
    id = fields.UUID(required=True)


class RegistrationSchema(Schema):
    tag = fields.Nested(TagSchema(), required=True)
    device_id = fields.UUID(required=True)
    mode = fields.Bool(truthy={True}, falsy={False}, required=True)


class UpdateSchema(Schema):
    device_id = fields.UUID(required=True)
    mode = fields.Bool(truthy={True}, falsy={False}, required=True)
