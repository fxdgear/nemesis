#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import calendar
import json

import dacite
from elasticsearch import RequestError, NotFoundError
from typing import Optional
from dataclasses import dataclass, field, asdict
from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.querydsl import QueryDSL
from nemesis.schemas.elasticsearch.transform import TransformSchema
from nemesis.resources.elasticsearch.index import Index
from nemesis.resources.elasticsearch.ingest_pipeline import IngestPipeline


@enforce_types
@dataclass(frozen=True)
class Dest(BaseResource):
    index: str
    pipeline: Optional[str] = None


@enforce_types
@dataclass(frozen=True)
class Latest(BaseResource):
    sort: str
    unique_key: list[str]


@enforce_types
@dataclass(frozen=True)
class Pivot(BaseResource):
    aggregations: dict
    group_by: dict


@enforce_types
@dataclass(frozen=True)
class RetentionPolicyTime(BaseResource):
    field: str
    max_age: str


@enforce_types
@dataclass(frozen=True)
class RetentionPolicy(BaseResource):
    time: RetentionPolicyTime


@enforce_types
@dataclass(frozen=True)
class Settings(BaseResource):
    docs_per_second: Optional[float]
    dates_as_epoch_millis: Optional[bool]
    align_checkpoints: Optional[bool]
    max_page_search_size: Optional[int]


@enforce_types
@dataclass(frozen=True)
class SyncTime(BaseResource):
    field: str
    delay: str = "60s"


@enforce_types
@dataclass(frozen=True)
class Sync(BaseResource):
    time: SyncTime


@enforce_types
@dataclass(frozen=True)
class Source(BaseResource):
    """
    Source is a required parameter of Transform
    https://www.elastic.co/guide/en/elasticsearch/reference/current/put-transform.html#put-transform-request-body
    """

    index: list
    runtime_mappings: Optional[dict] = None
    query: Optional[QueryDSL] = None


@dataclass(repr=False, frozen=True)
class Transform(BaseResource):
    """
    https://www.elastic.co/guide/en/elasticsearch/reference/current/put-transform.html#put-transform-request-body
    """

    source: Source
    dest: Dest
    id: Optional[str] = None
    pivot: Optional[Pivot] = None
    latest: Optional[Latest] = None
    sync: Optional[Sync] = None
    retention_policy: Optional[RetentionPolicy] = None
    settings: Optional[Settings] = None
    description: Optional[str] = None
    frequency: str = "1m"

    def __post_init__(self):
        if self.pivot is None and self.latest is None:
            raise TypeError("Value needed for `latest` or `pivot` field")

    @classmethod
    def get(cls, client, transform_id):
        """
        Get a transform from Elasticsearch
        """
        try:
            rt = client.transform.get_transform(transform_id=transform_id)
        except NotFoundError:
            return None
        transforms = rt["transforms"]
        ret = []
        for transform in transforms:
            ret.append(cls.fromdict(schemaclass=TransformSchema, body=transform))
        if len(ret) > 1:
            return ret
        else:
            return ret[0]

    def create(self, client, defer_validation=False, *args, **kwargs):
        try:
            ret = client.transform.put_transform(
                transform_id=self.id,
                body=self.asdict(),
                defer_validation=defer_validation,
                request_timeout=90,
                *args,
                **kwargs,
            )
        except RequestError as e:
            raise e
        return ret

    def delete(self, client, force=False, *args, **kwargs):
        try:
            return client.transform.delete_transform(
                transform_id=self.id, force=force, *args, **kwargs
            )
        except Exception as e:
            raise e

    def stop(
        self,
        client,
        allow_no_match=True,
        force=False,
        timeout="30s",
        wait_for_checkpoint=False,
        wait_for_completion=False,
        *args,
        **kwargs,
    ):
        try:
            return client.transform.stop_transform(
                transform_id=self.id,
                allow_no_match=allow_no_match,
                force=force,
                timeout=timeout,
                wait_for_checkpoint=wait_for_checkpoint,
                wait_for_completion=wait_for_completion,
                *args,
                **kwargs,
            )
        except Exception as e:
            raise e

    def start(self, client, timeout="30s", *args, **kwargs):
        try:
            return client.transform.start_transform(
                transform_id=self.id, timeout=timeout, *args, **kwargs
            )
        except Exception as e:
            raise e

    def update(self, client, *args, **kwargs):
        return self.create(client)
