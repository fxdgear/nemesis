#!/usr/bin/env python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, pre_load
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema
from nemesis.schemas.elasticsearch.alias import AliasSchema


class IndexSettingsSchema(Schema):
    index = fields.Dict()


class IndexSchema(Schema):
    name = fields.Str()
    aliases = fields.Nested(AliasSchema)
    settings = fields.Nested(IndexSettingsSchema)
    mappings = fields.Dict()

    def _remove_empty_values(self, data):
        for k, v in data.items():
            if not v:
                data[k] = None
        return data
