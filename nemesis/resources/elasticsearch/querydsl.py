#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from dataclasses import dataclass
from typing import Optional, Dict, cast

from nemesis.resources import enforce_types, BaseResource


@enforce_types
@dataclass(frozen=True)
class QueryDSL(BaseResource):
    id: Optional[str] = None
    bool: Optional[dict] = None
    boolstring: Optional[dict] = None
    common: Optional[dict] = None
    constant_score: Optional[dict] = None
    custom_filters_score: Optional[dict] = None
    dis_max: Optional[dict] = None
    distance_feature: Optional[dict] = None
    exists: Optional[dict] = None
    field: Optional[dict] = None
    function_score: Optional[dict] = None
    fuzzy: Optional[dict] = None
    geo_shape: Optional[dict] = None
    has_child: Optional[dict] = None
    has_parent: Optional[dict] = None
    ids: Optional[dict] = None
    indices: Optional[dict] = None
    match: Optional[dict] = None
    match_all: Optional[dict] = None
    match_phrase: Optional[dict] = None
    match_phrase_prefix: Optional[dict] = None
    nested: Optional[dict] = None
    percolate: Optional[dict] = None
    prefix: Optional[dict] = None
    query_string: Optional[dict] = None
    range: Optional[dict] = None
    regexp: Optional[dict] = None
    script: Optional[dict] = None
    simple_query_string: Optional[dict] = None
    span_containing: Optional[dict] = None
    span_first: Optional[dict] = None
    span_multi: Optional[dict] = None
    span_near: Optional[dict] = None
    span_not: Optional[dict] = None
    span_or: Optional[dict] = None
    span_term: Optional[dict] = None
    span_within: Optional[dict] = None
    term: Optional[dict] = None
    wildcard: Optional[dict] = None
    wrapper: Optional[dict] = None

    def asdict(self):
        """
        The "id" field isn't part of the actual body sent to Elasticsearch.
        But it's nice to have on the object we are dealing with.
        """
        d = super().asdict()
        d.pop("id")
        return d
