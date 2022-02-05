#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.index import (
    Index,
    IndexSettings,
)
from elasticsearch import Elasticsearch, RequestError, NotFoundError
from nemesis.exceptions import MultipleObjectsReturned
from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def index(es_client):
    indexsettings = IndexSettings(
        index={
            "routing": {
                "allocation": {"include": {"_tier_preference": "data_content"}}
            },
            "number_of_shards": "1",
            "number_of_replicas": "2",
        }
    )
    index = Index(name="test-index", settings=indexsettings)
    yield index
    # clear remote resources if they exist
    try:
        result = index.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


def test_asdict(index):
    """
    asdict method pop's the `name` field from the object to match
    how it would be sent or received from Elasticsearch
    """
    assert index.asdict() == {
        "settings": {
            "index": {
                "routing": {
                    "allocation": {"include": {"_tier_preference": "data_content"}}
                },
                "number_of_shards": "1",
                "number_of_replicas": "2",
            }
        }
    }


def test_id(index):
    assert index.id == "test-index"


def test_create_get_update_delete(index, es_client):
    assert Index.get(es_client, index.id) is None

    result = index.create(es_client)
    assert result == {
        "acknowledged": True,
        "index": "test-index",
        "shards_acknowledged": True,
    }

    result = Index.get(es_client, index.id)
    assert result.asdict() == index.asdict()

    with pytest.raises(RequestError):
        result = index.create(es_client)

    result = index.delete(es_client)
    assert result == {"acknowledged": True}
