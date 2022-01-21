#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from marshmallow import Schema, fields, pre_load, EXCLUDE
from nemesis.schemas.elasticsearch.querydsl import QueryDSLSchema


class Trigger(Schema):
    schedule = fields.Dict()


class Body(Schema):
    query = fields.Nested(QueryDSLSchema)
    size = fields.Int()
    sort = fields.Dict()


class SearchTemplate(Schema):
    id = fields.Str()
    params = fields.Dict()


class SearchRequest(Schema):
    indices = fields.List(fields.Str())
    body = fields.Nested(Body)
    template = fields.Nested(SearchTemplate)


class Search(Schema):
    request = fields.Nested(SearchRequest)
    extract = fields.List(fields.Str())


class HttpRequest(Schema):
    scheme = fields.Str()
    host = fields.Str()
    port = fields.Int()
    path = fields.Str()
    url = fields.Str()
    method = fields.Str()
    body = fields.Str()
    params = fields.Dict()
    headers = fields.Dict()
    auth = fields.Dict()
    proxy = fields.Dict()
    connection_timeout = fields.Str()
    read_timeout = fields.Str()
    extract = fields.List(fields.Str())
    response_content_type = fields.Str()


class Http(Schema):
    request = fields.Nested(HttpRequest)


class Chain(Schema):
    inputs = fields.List(fields.Dict())


class Input(Schema):
    simple = fields.Dict()
    search = fields.Nested(Search)
    http = fields.Nested(Http)
    chain = fields.Nested(Chain)


class Condition(Schema):
    always = fields.Dict()
    never = fields.Dict()
    compare = fields.Dict()
    array_compare = fields.Dict()
    script = fields.Dict()


class EmailAction(Schema):
    id = fields.Str()


class WatchSchema(Schema):
    watch_id = fields.Str()
    trigger = fields.Dict()
    input = fields.Dict()
    condition = fields.Dict()
    actions = fields.Dict()
    metadata = fields.Dict()
    throttle_period = fields.Int()
    throttle_period_in_millis = fields.Int()

    class Meta:
        unknown = EXCLUDE

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        watch = data["watch"]
        watch_id = data["_id"]
        watch["watch_id"] = watch_id
        return watch
