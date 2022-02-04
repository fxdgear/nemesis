#!/usr/bin/env python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, pre_load
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema
from nemesis.schemas.elasticsearch.alias import AliasSchema
from nemesis.schemas.elasticsearch.index import IndexSettingsSchema


class TemplateSchema(Schema):
    settings = fields.Nested(IndexSettingsSchema(), data_key="settings")
    mappings = fields.Dict()
    aliases = fields.Nested(AliasSchema(), data_key="aliases")


class IndexTemplateSchema(Schema):
    index_patterns = fields.List(fields.Str())
    template = fields.Nested(TemplateSchema())
    version = fields.Int()
    priority = fields.Int()
    composed_of = fields.List(fields.Str(), allow_none=True)
    version = fields.Int()
    meta = fields.Dict(data_key="_meta")
    name = fields.Str()

    def _remove_empty_values(self, data):
        for k, v in data.items():
            if not v:
                data[k] = None
        return data

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        index_template = data.pop("index_template")
        data.update(index_template)
        data = self._remove_empty_values(data)
        return data
