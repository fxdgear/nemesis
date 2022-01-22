#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
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

def _get():
    """
    get_index_template returns a list of objects regardless of if you ask for one or many in
    a glob form.

    This does not match the way you "send" an index template. The body of sending an index template
    matches the dataclass definition.

    The dataclass/serializer must be able to transform the object received from Elasticsearch
    and convert it to an object which matches the dataclass for IndexTemplate, which is the structure
    of the json object as it is sent to Elasticsearch for creation.
    """

    def mock_get_index_template(name):
        return {
            "index_templates": [
                {
                    "name": "test-template",
                    "index_template": {
                        "index_patterns": ["foo-bar", "bar-foo-*"],
                        "template": {
                            "settings": {"index": {"number_of_shards": "1"}},
                            "mappings": {
                                "_source": {"enabled": True},
                                "properties": {
                                    "created_at": {
                                        "format": "EEE MMM dd HH:mm:ss Z yyyy",
                                        "type": "date",
                                    },
                                    "host_name": {"type": "keyword"},
                                },
                            },
                        },
                        "composed_of": [],
                    },
                }
            ]
        }

    client = MagicMock()
    client.indices.get_index_template = mock_get_index_template

    template = IndexTemplate.get(client, "index-template")
    assert template.asdict() == {
        "index_patterns": ["foo-bar", "bar-foo-*"],
        "template": {
            "settings": {"index": {"number_of_shards": "1"}},
            "mappings": {
                "_source": {"enabled": True},
                "properties": {
                    "created_at": {
                        "format": "EEE MMM dd HH:mm:ss Z yyyy",
                        "type": "date",
                    },
                    "host_name": {"type": "keyword"},
                },
            },
        },
    }

