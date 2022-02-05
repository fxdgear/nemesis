#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.index import Index
from nemesis.resources.elasticsearch.ingest_pipeline import IngestPipeline
from nemesis.resources.elasticsearch.transform import (
    Transform,
    Source,
    QueryDSL,
    Dest,
    Sync,
    SyncTime,
    Pivot,
    RetentionPolicy,
    RetentionPolicyTime,
)
from elasticsearch import Elasticsearch, RequestError, NotFoundError
from nemesis.tests.resources.elasticsearch.test_ingest_pipeline import pipeline
from nemesis.tests import es_client, nemesis_client
from nemesis.schemas.elasticsearch.transform import TransformSchema


@pytest.fixture
def dest_index(es_client):
    index = Index(name="kibana_sample_data_ecommerce_transform1")
    yield index

    # clear remote resources if they exist
    try:
        result = index.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


@pytest.fixture
def source_index(es_client):
    index = Index(name="kibana_sample_data_ecommerce")
    yield index

    # clear remote resources if they exist
    try:
        result = index.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


@pytest.fixture
def transform(es_client, dest_index, source_index, pipeline):
    transform = Transform(
        id="test-transform",
        description="Maximum priced ecommerce data by customer_id in Asia",
        retention_policy=RetentionPolicy(
            time=RetentionPolicyTime(field="order_date", max_age="30d")
        ),
        dest=Dest(index=dest_index.id, pipeline=pipeline.id),
        pivot=Pivot(
            group_by={"customer_id": {"terms": {"field": "customer_id"}}},
            aggregations={"max_price": {"max": {"field": "taxful_total_price"}}},
        ),
        sync=Sync(
            time=SyncTime(field="order_date", delay="60s"),
        ),
        frequency="5m",
        source=Source(
            index=[
                source_index.id,
            ],
            query=QueryDSL(term={"geoip.continent_name": {"value": "Asia"}}),
        ),
    )
    yield transform

    # clear remote resources if they exist
    try:
        result = transform.delete(es_client)
        assert result == {"acknowledged": True}
    except NotFoundError:
        pass


def test_latest_or_pivot(source_index, dest_index, pipeline):
    with pytest.raises(TypeError):
        Transform(
            id="test-transform",
            description="Maximum priced ecommerce data by customer_id in Asia",
            retention_policy=RetentionPolicy(
                time=RetentionPolicyTime(field="order_date", max_age="30d")
            ),
            dest=Dest(index=dest_index.id, pipeline=pipeline.id),
            sync=Sync(
                time=SyncTime(field="order_date", delay="60s"),
            ),
            frequency="5m",
            source=Source(
                index=[
                    source_index.id,
                ],
                query=QueryDSL(term={"geoip.continent_name": {"value": "Asia"}}),
            ),
        )


def test_asdict(transform):
    """ """
    assert transform.asdict() == {
        "source": {
            "index": ["kibana_sample_data_ecommerce"],
            "query": {"term": {"geoip.continent_name": {"value": "Asia"}}},
        },
        "dest": {
            "index": "kibana_sample_data_ecommerce_transform1",
            "pipeline": "test-pipeline",
        },
        "id": "test-transform",
        "pivot": {
            "aggregations": {"max_price": {"max": {"field": "taxful_total_price"}}},
            "group_by": {"customer_id": {"terms": {"field": "customer_id"}}},
        },
        "sync": {"time": {"field": "order_date", "delay": "60s"}},
        "retention_policy": {"time": {"field": "order_date", "max_age": "30d"}},
        "description": "Maximum priced ecommerce data by customer_id in Asia",
        "frequency": "5m",
    }


def test_frozen_object(transform):
    with pytest.raises(FrozenInstanceError):
        transform.processors = [{}]


def test_id(transform):
    assert transform.id == "test-transform"


def test_get_not_found(es_client):
    assert Transform.get(es_client, "notfound") is None


def test_create_multiple(es_client, transform, source_index, dest_index, pipeline):
    result = dest_index.create(es_client)
    assert result == {
        "acknowledged": True,
        "shards_acknowledged": True,
        "index": "kibana_sample_data_ecommerce_transform1",
    }
    result = source_index.create(es_client)
    assert result == {
        "acknowledged": True,
        "shards_acknowledged": True,
        "index": "kibana_sample_data_ecommerce",
    }

    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}

    result = transform.create(es_client)
    assert result == {"acknowledged": True}

    with pytest.raises(RequestError):
        transform.create(es_client)


def test_create_update_delete(transform, dest_index, source_index, pipeline, es_client):
    result = dest_index.create(es_client)
    assert result == {
        "acknowledged": True,
        "shards_acknowledged": True,
        "index": "kibana_sample_data_ecommerce_transform1",
    }
    result = source_index.create(es_client)
    assert result == {
        "acknowledged": True,
        "shards_acknowledged": True,
        "index": "kibana_sample_data_ecommerce",
    }

    result = pipeline.create(es_client)
    assert result == {"acknowledged": True}

    result = transform.create(es_client)
    assert result == {"acknowledged": True}

    result = Transform.get(es_client, transform.id)
    assert result == transform

    t = transform.asdict()
    t["description"] = "change me"
    new_transform = Transform.fromdict(schemaclass=TransformSchema, body=t)

    with pytest.raises(RequestError):
        new_transform.update(es_client)

    result = transform.delete(es_client)
    assert result == {"acknowledged": True}
