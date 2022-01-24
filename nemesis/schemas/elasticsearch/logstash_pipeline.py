#!/usr/bin/env python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, pre_load


class LogstashPipelineSchema(Schema):
    id = fields.Str()
    description = fields.Str()
    username = fields.Str()
    last_modified = fields.DateTime()
    pipeline = fields.Str()
    pipeline_metadata = fields.Dict()
    pipeline_settings = fields.Dict()

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        keys = list(data.keys())
        pipeline_id = keys[0]
        data = data.pop(pipeline_id)
        data["id"] = pipeline_id
        return data
