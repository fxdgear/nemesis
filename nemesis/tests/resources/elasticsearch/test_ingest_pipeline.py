#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.ingest_pipeline import IngestPipeline
from elasticsearch import Elasticsearch, RequestError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def pipeline():
    return IngestPipeline(
        id="test-pipeline",
        processors=[
            {"pipeline": {"name": "pipelineA"}},
            {"set": {"field": "outer_pipeline_set", "value": "outer"}},
        ],
    )


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


def test_create_update_delete(pipeline, es_client):
    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}

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
