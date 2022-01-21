#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Optional

from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.querydsl import QueryDSL


@enforce_types
@dataclass(frozen=True)
class Alias(BaseResource):
    filter: Optional[QueryDSL]
    index_routing: Optional[str]
    is_hidden: Optional[bool]
    is_write_index: Optional[bool]
    routing: Optional[str]
    search_routing: Optional[str]
