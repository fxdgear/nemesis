#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from dataclasses import dataclass
from typing import Optional, Dict, cast

from nemesis.resources import enforce_types, BaseResource


@enforce_types
@dataclass(frozen=True)
class QueryDSL(BaseResource):
    """
    Manage a query for Elasticsearch

    :param id: Unique ID for a query.
    :type id: str, optional

    :param bool: Bool query
    :type bool: dict, optional

    :param boolstring: boolstring query
    :type boolstring: dict, optional

    :param common: Common query
    :type common: dict, optional

    :param constant_score: Constant score query
    :type constant_score: dict, optional

    :param custom_filters_score: custom filters score query
    :type custom_filters_score: dict, optional

    :param dis_max: dis_max query
    :type dis_max: dict, optional

    :param distance_feature: distance feature query
    :type distance_feature: dict, optional

    :param exists: exists query
    :type exists: dict, optional

    :param field: Field query
    :type field: dict, optional

    :param function_score: function score query
    :type function_score: dict, optional

    :param fuzzy: fuzzy query
    :type fuzzy: dict, optional

    :param geo_shape: geo_shape query
    :type geo_shape: dict, optional

    :param has_child: has child query
    :type has_child: dict, optional

    :param has_parent: has_parent query
    :type has_parent: dict, optional

    :param ids: IDs query
    :type ids: dict, optional

    :param indices: indices query
    :type indices: dict, optional

    :param match: Match query
    :type match: dict, optional

    :param match_all: Match all query
    :type match_all: dict, optional

    :param match_phrase: match_phrase query
    :type match_phrase: dict, optional

    :param match_phrase_prefix: Match phrase prefix query
    :type match_phrase_prefix: dict, optional

    :param nested: Nested query
    :type nested: dict, optional

    :param percolate: percolate query
    :type percolate: dict, optional

    :param prefix: Prefix query
    :type prefix: dict, optional

    :param query_string: query string query
    :type query_string: dict, optional

    :param range: range query
    :type range: dict, optional

    :param regexp: Regex query
    :type regexp: dict, optional

    :param script: script
    :type script: dict, optional

    :param simple_query_string: simple_query_string query
    :type simple_query_string: dict, optional

    :param span_containing: span containing query
    :type span_containing: dict, optional

    :param span_first: span first query
    :type span_first: dict, optional

    :param span_multi: span multi query
    :type span_multi: dict, optional

    :param span_near: span near query
    :type span_near: dict, optional

    :param span_not: span not query
    :type span_not: dict, optional

    :param span_or: span or query
    :type span_or: dict, optional

    :param span_term: Span term query
    :type span_term: dict, optional

    :param span_within: Span within query
    :type span_within: dict, optional

    :param term: Term query
    :type term: dict, optional

    :param wildcard: Wildcard Query
    :type wildcard: dict, optional

    :param wrapper: Wrapper query
    :type wrapper: dict, optional

    """

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
