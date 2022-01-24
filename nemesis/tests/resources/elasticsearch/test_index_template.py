#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.index_template import IndexTemplate, Template
from elasticsearch import Elasticsearch, RequestError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def template():
    return IndexTemplate(
        name="test-template",
        index_patterns=["test-foo"],
        template=Template(settings={"number_of_replicas": 2}, mappings={}),
    )


def test_asdict(template):
    """
    asdict method pop's the `name` field from the object to match
    how it would be sent or received from Elasticsearch
    """

    assert template.asdict() == {
        "index_patterns": ["test-foo"],
        "template": {
            "settings": {"number_of_replicas": 2},
            "mappings": {},
        },
    }


def test_frozen_object(template):
    with pytest.raises(FrozenInstanceError):
        template.index_patterns = ["raise-error"]


def test_id(template):
    assert template.id == "test-template"


def test_create_update_delete(template, es_client):
    result = template.create(es_client)
    assert result == {"acknowledged": True}

    with pytest.raises(RequestError):
        result = template.create(es_client)

    template.index_patterns.append("foo-*")
    result = template.update(es_client)
    assert result == {"acknowledged": True}

    result = template.delete(es_client)
    assert result == {"acknowledged": True}
