#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from marshmallow import Schema, fields, pre_load
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema


class SyncTimeSchema(Schema):
    field = fields.Str()
    delay = fields.Str(default="60s")


class SyncSchema(Schema):
    time = fields.Nested(SyncTimeSchema)


class RetentionPolicyTimeSchema(Schema):
    field = fields.Str()
    max_age = fields.Str()


class RetentionPolicySchema(Schema):
    time = fields.Nested(RetentionPolicyTimeSchema, load_from="time")


class SettingsSchema(Schema):
    dates_as_epoc_millis = fields.Boolean(default=False)
    docs_per_second = fields.Float()
    align_checkpoints = fields.Boolean(default=True)
    max_page_search_size = fields.Integer(default=500)


class LatestSchema(Schema):
    sort = fields.Str()
    unique_key = fields.List(fields.Str())


class PivotSchema(Schema):
    aggregations = fields.Dict()
    group_by = fields.Dict()
    max_page_search_size = fields.Integer(default=500)


class DestSchema(Schema):
    index = fields.Str()
    pipeline = fields.Str()


class SourceSchema(Schema):
    index = fields.List(fields.Str())
    runtime_mappings = fields.Dict()
    query = fields.Nested(QueryDSLSchema(), load_from="query")


class TransformSchema(Schema):
    # fmt: off
    source = fields.Nested(SourceSchema, load_from="source")
    dest = fields.Nested(DestSchema, load_from="dest")
    pivot = fields.Nested(PivotSchema, load_from="pivot")
    latest = fields.Nested(LatestSchema, load_from="latest")
    sync = fields.Nested(SyncSchema, load_from="sync")
    retention_policy = fields.Nested(RetentionPolicySchema, load_from="retention_policy")
    settings = fields.Nested(SettingsSchema, load_from="settings", allow_none=True)
    description = fields.Str()
    frequency = fields.Str()
    version = fields.Str()
    create_time = fields.Int()
    version = fields.Str()
    id = fields.Str()
    # fmt: on

    @pre_load
    def remove_empty_values(self, data, *args, **kwargs):
        for k, v in data.items():
            if not v:
                data[k] = None
        return data
