#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Optional

from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.querydsl import QueryDSL


@enforce_types
@dataclass(frozen=True)
class Alias(BaseResource):
    """
    Manage an `Elasticsearch Index <https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-aliases.html>`_

    :param filter: Query used to limit documents the alias can access.
    :type filter: QueryDSL, optional

    :param index_routing: Value used to route indexing operations to a specific shard. If specified, this overwrites the routing value for indexing operations. Data stream aliases don’t support this parameter.
    :type index_routing: str, optional

    :param is_hidden: If true, the alias is hidden. Defaults to false. All data streams or indices for the alias must have the same is_hidden value.
    :type is_hidden: bool, optional

    :param is_write_index: If true, sets the write index or data stream for the alias.
    :type is_write_index: bool, optional

    :param routing: Value used to route indexing and search operations to a specific shard. Data stream aliases don’t support this parameter.
    :type routing: str, optional

    :param search_routing: Value used to route search operations to a specific shard. If specified, this overwrites the routing value for search operations. Data stream aliases don’t support this parameter.
    :type search_routing: str, optional
    """

    filter: Optional[QueryDSL]
    index_routing: Optional[str]
    is_hidden: Optional[bool]
    is_write_index: Optional[bool]
    routing: Optional[str]
    search_routing: Optional[str]
