#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.ingest_pipeline import IngestPipeline
from elasticsearch import Elasticsearch, RequestError, NotFoundError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def pipeline(es_client):
    pipeline = IngestPipeline(
        id="test-pipeline",
        processors=[
            {"pipeline": {"name": "pipelineA"}},
            {"set": {"field": "outer_pipeline_set", "value": "outer"}},
        ],
    )
    yield pipeline

    # clear remote resources if they exist
    try:
        result = pipeline.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


def test_asdict(pipeline):
    """ """
    assert pipeline.asdict() == {
        "id": "test-pipeline",
        "processors": [
            {"pipeline": {"name": "pipelineA"}},
            {"set": {"field": "outer_pipeline_set", "value": "outer"}},
        ],
    }


def test_frozen_object(pipeline):
    with pytest.raises(FrozenInstanceError):
        pipeline.processors = [{}]


def test_id(pipeline):
    assert pipeline.id == "test-pipeline"


def test_get_not_found(es_client):
    assert IngestPipeline.get(es_client, "notfound") is None


def test_create_multiple(es_client, pipeline):
    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}

    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}


def test_create_update_delete(pipeline, es_client):
    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}

    result = IngestPipeline.get(es_client, pipeline.id)
    assert result == pipeline

    # Test that create called multiple times is ok.
    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}

    pipeline.processors.append(
        {"set": {"field": "inner_pipeline_set", "value": "inner"}}
    )
    result = pipeline.update(es_client)
    assert result == {"acknowledged": True}

    result = pipeline.delete(es_client)
    assert result == {"acknowledged": True}
