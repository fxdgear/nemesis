#!/usr/bin/env python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema


class AliasSchema(Schema):
    filter = fields.Nested(QueryDSLSchema(), data_key="filter")
    index_routing = fields.Str()
    is_hidden = fields.Bool()
    is_write_index = fields.Bool()
    routing = fields.Str()
    search_routing = fields.Str()
