#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import MagicMock
from nemesis import Nemesis
from elasticsearch import Elasticsearch
from nemesis.resources.elasticsearch.index_template import Template


CLOUD_ID = "not-a-real-deployment:ZXUtd2VzdC0xLmF3cy5mb3VuZC5pbyRlOTY1NjUwNzU4Y2Y0ODAzYjZlNWJkNWZkNDZjNzI3ZCQzMGY5OGQyZTMwOGI0OGUwODNhM2I2ODEwMGU1MTU0MQ=="
ES_HOST = "http://localhost:9200"
USERNAME = "elastic"
PASSWORD = "changeme"

def test_init_nemesis_cloud_id():
    n = Nemesis(username=USERNAME, password=PASSWORD, cloud_id=CLOUD_ID)
    assert isinstance(n.client, Elasticsearch)


def test_init_nemesis_url():
    n = Nemesis(username=USERNAME, password=PASSWORD, es_host=ES_HOST)
    assert isinstance(n.client, Elasticsearch)


def test_get_client_for_resource():
    template = Template()
    n = Nemesis(username=USERNAME, password=PASSWORD, cloud_id=CLOUD_ID)
    assert n.get_client_for(template) == n.client


def test_register_resource():
    resource = MagicMock()
    resource.get.return_value = Template()
    n = Nemesis(username=USERNAME, password=PASSWORD, es_host=ES_HOST)
    n.register(resource)
    assert len(n.resources) == 1
    r = n.resources[0]
    assert r["force"] is False
    assert r["post_deploy"] is None
    assert r["pre_deploy"] is None
