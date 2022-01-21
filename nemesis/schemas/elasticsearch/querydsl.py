#!/usr/bin/env python
# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class QueryDSLSchema(Schema):
    bool = fields.Dict()
    boolstring = fields.Dict()
    common = fields.Dict()
    constant_score = fields.Dict()
    custom_filters_score = fields.Dict()
    dis_max = fields.Dict()
    distance_feature = fields.Dict()
    exists = fields.Dict()
    field = fields.Dict()
    function_score = fields.Dict()
    fuzzy = fields.Dict()
    geo_shape = fields.Dict()
    has_child = fields.Dict()
    has_parent = fields.Dict()
    ids = fields.Dict()
    indices = fields.Dict()
    match = fields.Dict()
    match_all = fields.Dict()
    match_phrase = fields.Dict()
    match_phrase_prefix = fields.Dict()
    nested = fields.Dict()
    percolate = fields.Dict()
    prefix = fields.Dict()
    query_string = fields.Dict()
    range = fields.Dict()
    regexp = fields.Dict()
    script = fields.Dict()
    simple_query_string = fields.Dict()
    span_containing = fields.Dict()
    span_first = fields.Dict()
    span_multi = fields.Dict()
    span_near = fields.Dict()
    span_not = fields.Dict()
    span_or = fields.Dict()
    span_term = fields.Dict()
    span_within = fields.Dict()
    wildcard = fields.Dict()
    wrapper = fields.Dict()
