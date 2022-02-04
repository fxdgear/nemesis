#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import datetime
import pytz
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.logstash_pipeline import LogstashPipeline
from elasticsearch import Elasticsearch, RequestError, NotFoundError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def pipeline(es_client):
    pipeline = LogstashPipeline(
        id="test-pipeline",
        username="elastic",
        last_modified=datetime.datetime(2022, 3, 3, 0, 0, 0, 0, pytz.UTC),
        pipeline="",
        pipeline_metadata={},
        pipeline_settings={},
    )
    yield pipeline

    # clear remote resources if they exist
    try:
        result = pipeline.delete(es_client)
        assert result == ""
    except NotFoundError:
        pass


def test_asdict(pipeline):
    """ """
    assert pipeline.asdict() == {
        "id": "test-pipeline",
        "last_modified": "2022-03-03T00:00:00.000Z",
        "pipeline": "",
        "pipeline_metadata": {},
        "pipeline_settings": {},
        "username": "elastic",
    }


def test_frozen_object(pipeline):
    with pytest.raises(FrozenInstanceError):
        pipeline.pipeline = "test"


def test_id(pipeline):
    assert pipeline.id == "test-pipeline"


def test_get_not_found(es_client):
    assert LogstashPipeline.get(es_client, "notfound") is None


def test_create_multiple(es_client, pipeline):
    result = pipeline.create(es_client)
    assert result == ""

    result = pipeline.create(es_client)
    assert result == ""


def test_create_update_delete(pipeline, es_client):
    result = pipeline.create(es_client)
    assert result == ""

    result = LogstashPipeline.get(es_client, pipeline.id)
    assert result == pipeline

    # Test that create called multiple times is ok.
    result = pipeline.create(es_client)
    assert result == ""

    new_pipeline = LogstashPipeline(
        id="test-pipeline",
        username="elastic",
        last_modified=datetime.datetime(2022, 3, 14),
        pipeline="test",
        pipeline_metadata={},
        pipeline_settings={},
    )
    result = new_pipeline.update(es_client)
    assert result == ""

    result = pipeline.delete(es_client)
    assert result == ""
