#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from marshmallow import Schema, fields, pre_load
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema
from nemesis.schemas.elasticsearch.index import IndexSchema
from nemesis.schemas.elasticsearch.ingest_pipeline import IngestPipelineSchema


class SyncTimeSchema(Schema):
    field = fields.Str()
    delay = fields.Str(dump_default="60s")


class SyncSchema(Schema):
    time = fields.Nested(SyncTimeSchema)


class RetentionPolicyTimeSchema(Schema):
    field = fields.Str()
    max_age = fields.Str()


class RetentionPolicySchema(Schema):
    time = fields.Nested(RetentionPolicyTimeSchema, data_key="time")


class SettingsSchema(Schema):
    dates_as_epoc_millis = fields.Boolean(dump_default=False)
    docs_per_second = fields.Float()
    align_checkpoints = fields.Boolean(dump_default=True)
    max_page_search_size = fields.Integer(dump_default=500)


class LatestSchema(Schema):
    sort = fields.Str()
    unique_key = fields.List(fields.Str())


class PivotSchema(Schema):
    aggregations = fields.Dict()
    group_by = fields.Dict()
    max_page_search_size = fields.Integer()


class DestSchema(Schema):
    index = fields.Str()
    pipeline = fields.Str()


class SourceSchema(Schema):
    index = fields.List(fields.Str())
    runtime_mappings = fields.Dict()
    query = fields.Nested(QueryDSLSchema(), data_key="query")


class TransformSchema(Schema):
    # fmt: off
    source = fields.Nested(SourceSchema, data_key="source")
    dest = fields.Nested(DestSchema, data_key="dest")
    pivot = fields.Nested(PivotSchema, data_key="pivot")
    latest = fields.Nested(LatestSchema, data_key="latest")
    sync = fields.Nested(SyncSchema, data_key="sync")
    retention_policy = fields.Nested(RetentionPolicySchema, data_key="retention_policy")
    settings = fields.Nested(SettingsSchema, data_key="settings", allow_none=True)
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
