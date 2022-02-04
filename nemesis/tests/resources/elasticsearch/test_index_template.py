#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.index_template import (
    IndexTemplate,
    Template,
    IndexSettings,
)
from elasticsearch import Elasticsearch, RequestError, NotFoundError
from nemesis.exceptions import MultipleObjectsReturned
from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def template(es_client):
    template = IndexTemplate(
        name="test-template",
        index_patterns=["test-foo"],
        template=Template(
            settings=IndexSettings(index={"number_of_replicas": "2"}),
        ),
    )
    yield template
    # clear remote resources if they exist
    try:
        result = template.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


@pytest.fixture
def template2(es_client):
    template = IndexTemplate(
        name="test-template-2",
        index_patterns=["test-bar"],
        template=Template(settings=IndexSettings(index={"number_of_replicas": 2})),
    )
    yield template
    # clear remote resources if they exist
    try:
        result = template.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


def test_asdict(template):
    """
    asdict method pop's the `name` field from the object to match
    how it would be sent or received from Elasticsearch
    """

    assert template.asdict() == {
        "index_patterns": ["test-foo"],
        "template": {
            "settings": {"index": {"number_of_replicas": "2"}},
        },
    }


def test_frozen_object(template):
    with pytest.raises(FrozenInstanceError):
        template.index_patterns = ["raise-error"]


def test_id(template):
    assert template.id == "test-template"


def test_get_multiple(template, template2, es_client):
    result = template.create(es_client)
    assert result == {"acknowledged": True}

    result = template2.create(es_client)
    assert result == {"acknowledged": True}

    with pytest.raises(MultipleObjectsReturned):
        IndexTemplate.get(es_client, "test-template*")


def test_create_get_update_delete(template, es_client):
    assert IndexTemplate.get(es_client, template.id) is None

    result = template.create(es_client)
    assert result == {"acknowledged": True}

    result = IndexTemplate.get(es_client, template.id)
    assert result.asdict() == template.asdict()

    with pytest.raises(RequestError):
        result = template.create(es_client)

    template.index_patterns.append("foo-*")
    result = template.update(es_client)
    assert result == {"acknowledged": True}

    result = template.delete(es_client)
    assert result == {"acknowledged": True}
