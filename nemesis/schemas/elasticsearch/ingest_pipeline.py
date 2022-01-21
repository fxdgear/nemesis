#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from marshmallow import Schema, fields, pre_load
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema


class IngestPipelineSchema(Schema):
    processors = fields.List(fields.Dict())
    description = fields.Str()
    on_failure = fields.List(fields.Dict())
    version = fields.Int()
    meta = fields.Dict(data_key="_meta")
    id = fields.Str()

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        keys = list(data.keys())
        pipeline_id = keys[0]
        data = data.pop(pipeline_id)
        data["id"] = pipeline_id
        return data
