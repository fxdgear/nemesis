#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import datetime
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.logstash_pipeline import LogstashPipeline
from elasticsearch import Elasticsearch, RequestError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def pipeline():
    return LogstashPipeline(
        id="test-pipeline",
        username="elastic",
        last_modified=datetime.datetime(2022, 3, 3),
        pipeline="",
        pipeline_metadata={},
        pipeline_settings={},
    )


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


def test_create_update_delete(pipeline, es_client):
    result = pipeline.create(es_client)
    assert result == ""

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
