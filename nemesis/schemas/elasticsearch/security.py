#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from marshmallow import Schema, fields, pre_load, EXCLUDE
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema


class ApplicationSchema(Schema):
    application = fields.Str()
    privileges = fields.List(fields.Str())
    resources = fields.List(fields.Str())


class IndexSchema(Schema):
    field_security = fields.Dict()
    names = fields.List(fields.Str())
    privileges = fields.List(fields.Str())
    query = fields.Nested(QueryDSLSchema, data_key="query")
    allow_restricted_indices = fields.Bool()


class RoleSchema(Schema):
    name = fields.Str()
    applications = fields.List(
        fields.Nested(ApplicationSchema, data_key="applications")
    )
    cluster = fields.List(fields.Str())
    _global = fields.Dict(data_key="global")
    indices = fields.List(fields.Nested(IndexSchema, data_key="indices"))
    metadata = fields.Dict()
    run_as = fields.List(fields.Str())

    class Meta:
        unknown = EXCLUDE

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        keys = list(data.keys())
        role_name = keys[0]
        data = data.pop(role_name)
        data["name"] = role_name
        for c, index in enumerate(data["indices"]):
            if isinstance(index["query"], str):
                index["query"] = json.loads(index["query"])
        return data


class RoleMappingSchema(Schema):
    name = fields.Str()
    enabled = fields.Boolean()
    roles = fields.List(fields.Str())
    role_templates = fields.List(fields.Dict())
    rules = fields.Dict()
    metadata = fields.Dict()

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        keys = list(data.keys())
        name = keys[0]
        data = data.pop(name)
        data["name"] = name
        return data
