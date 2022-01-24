#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.querydsl import QueryDSL
from elasticsearch import Elasticsearch, RequestError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def query():
    return QueryDSL(id="test-query", bool={"must": {"term": {"user.id": "kimchy"}}})


def test_asdict(query):
    """
    asdict method pop's the `name` field from the object to match
    how it would be sent or received from Elasticsearch
    """

    assert query.asdict() == {"bool": {"must": {"term": {"user.id": "kimchy"}}}}


def test_frozen_object(query):
    with pytest.raises(FrozenInstanceError):
        query.bool = {"must": {"term": {"user.id": "fxdgear"}}}


def test_id(query):
    assert query.id == "test-query"


def test_create_update_delete(query, es_client):
    pass
