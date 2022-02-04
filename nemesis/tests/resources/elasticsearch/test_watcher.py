#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.watcher import (
    Watch,
    Trigger,
    Input,
    Search,
    SearchRequest,
    Body,
    QueryDSL,
    Condition,
)

from elasticsearch import Elasticsearch, RequestError, NotFoundError
from nemesis.exceptions import MultipleObjectsReturned
from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def watch(es_client):
    watch = Watch(
        watch_id="test-watch",
        trigger=Trigger(schedule={"cron": "0 0/1 * * * ?"}),
        input=Input(
            search=Search(
                request=SearchRequest(
                    indices=[
                        "logstash*",
                    ],
                    body=Body(
                        query=QueryDSL(
                            bool={
                                "must": {"match": {"response": 404}},
                                "filter": {
                                    "range": {
                                        "@timestamp": {
                                            "from": "{{ctx.trigger.scheduled_time}}||-5m",
                                            "to": "{{ctx.trigger.triggered_time}}",
                                        }
                                    }
                                },
                            }
                        )
                    ),
                )
            )
        ),
        condition=Condition(compare={"ctx.payload.hits.total": {"gt": 0}}),
        actions={
            "email_admin": {
                "email": {
                    "profile": "standard",
                    "to": [
                        "admin@domain.host.com",
                    ],
                    "subject": "404 recently encountered",
                }
            }
        },
    )
    yield watch
    # clear remote resources if they exist
    try:
        result = watch.delete(es_client)
        assert result["found"]
    except NotFoundError:
        pass


def test_asdict(watch):
    """
    asdict method pop's the `name` field from the object to match
    how it would be sent or received from Elasticsearch
    """
    assert watch.asdict() == {
        "trigger": {"schedule": {"cron": "0 0/1 * * * ?"}},
        "input": {
            "search": {
                "request": {
                    "indices": ["logstash*"],
                    "body": {
                        "query": {
                            "bool": {
                                "must": {"match": {"response": 404}},
                                "filter": {
                                    "range": {
                                        "@timestamp": {
                                            "from": "{{ctx.trigger.scheduled_time}}||-5m",
                                            "to": "{{ctx.trigger.triggered_time}}",
                                        }
                                    }
                                },
                            }
                        }
                    },
                }
            }
        },
        "condition": {"compare": {"ctx.payload.hits.total": {"gt": 0}}},
        "actions": {
            "email_admin": {
                "email": {
                    "profile": "standard",
                    "to": [
                        "admin@domain.host.com",
                    ],
                    "subject": "404 recently encountered",
                }
            }
        },
    }


def test_frozen_object(watch):
    with pytest.raises(FrozenInstanceError):
        watch.index_patterns = ["raise-error"]


def test_id(watch):
    assert watch.id == "test-watch"


def test_create_get_update_delete(watch, es_client):
    assert Watch.get(es_client, watch.id) is None

    result = watch.create(es_client)
    assert result["created"]

    result = Watch.get(es_client, watch.id)
    assert result.asdict() == watch.asdict()

    result = watch.create(es_client)
    assert result["created"] is False

    result = watch.delete(es_client)
    assert result["found"]
