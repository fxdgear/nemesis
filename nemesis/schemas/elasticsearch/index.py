#!/usr/bin/env python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, pre_load
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema
from nemesis.schemas.elasticsearch.alias import AliasSchema


class IndexSettingsSchema(Schema):
    index = fields.Dict()

    @pre_load(pass_many=True)
    def remove_ignored_fields(self, data, many, **kwargs):
        ignored_fields = ["creation_date", "provided_name", "uuid", "version"]
        d = data["index"]

        for field in ignored_fields:
            if field in d.keys():
                d.pop(field)
        return data


class IndexSchema(Schema):
    name = fields.Str()
    aliases = fields.Nested(AliasSchema, data_key="aliases", allow_none=True)
    settings = fields.Nested(IndexSettingsSchema, data_key="settings", allow_none=True)
    mappings = fields.Dict(data_key="mappings", allow_none=True)

    def remove_empty_values(self, data):
        for k, v in data.items():
            if not v:
                data[k] = None
        return data

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        keys = list(data.keys())
        id = keys[0]
        data = data.pop(id)
        data["name"] = id
        data = self.remove_empty_values(data)
        return data
