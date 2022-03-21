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
    """
    Transform Destination

    :param index: Destination index to put transform results in.
    :type index: str

    :param pipeline: Optional Pipeline to ingest documents through.
    :type pipeline: str, optional
    """

    index: str
    pipeline: Optional[str] = None


@enforce_types
@dataclass(frozen=True)
class Latest(BaseResource):
    """
    Transform Latest

    :param sort:
    :type sort: str

    :param unique_key:
    :type unique_key: list, optional
    """

    sort: str
    unique_key: list


@enforce_types
@dataclass(frozen=True)
class Pivot(BaseResource):
    """
    Transform Pivot

    :param aggregations: Dictionary query of aggregations.
    :type aggregations: dict

    :param group_by:
    :type group_by: dict
    """

    aggregations: dict
    group_by: dict
    max_page_search_size: Optional[int] = None


@enforce_types
@dataclass(frozen=True)
class RetentionPolicyTime(BaseResource):
    """
    Transform RetentionPolicyTime

    :param field: Field name
    :type field: str

    :param max_age:
    :type max_age: str
    """

    field: str
    max_age: str


@enforce_types
@dataclass(frozen=True)
class RetentionPolicy(BaseResource):
    """
    Transform RetentionPolicyTime

    :param time: :py:mod:`RetentionPolicyTime`
    :type time: RetentionPolicyTime

    """

    time: RetentionPolicyTime


@enforce_types
@dataclass(frozen=True)
class Settings(BaseResource):
    """
    Transform Settings

    :param docs_per_second: Optional docs per second.
    :type docs_per_second: float, optional

    :param dates_as_epoch_millis: use epoch millisecond precision.
    :type dates_as_epoch_millis: bool, optional

    :param align_checkpoints: Align checkpoints.
    :type align_checkpoints: bool, optional

    :param max_page_search_size: Max page search size
    :type max_page_search_size: int, optional

    """

    docs_per_second: Optional[float]
    dates_as_epoch_millis: Optional[bool]
    align_checkpoints: Optional[bool]
    max_page_search_size: Optional[int]


@enforce_types
@dataclass(frozen=True)
class SyncTime(BaseResource):
    """
    Transform SyncTime

    :param field: Field name
    :type field: str

    :param delay:
    :type delay: str
    """

    field: str
    delay: str = "60s"


@enforce_types
@dataclass(frozen=True)
class Sync(BaseResource):
    """
    Transform Sync

    :param time: :py:mod:`SyncTime`
    :type time: SyncTime

    """

    time: SyncTime


@enforce_types
@dataclass(frozen=True)
class Source(BaseResource):
    """
    Source is a required parameter of `Transform <https://www.elastic.co/guide/en/elasticsearch/reference/current/put-transform.html#put-transform-request-body>`__

    :param index: List of inxex names
    :type index: list

    :param runtime_mappings: Optional runtime mappings to use for source.
    :type runtime_mappings: dict, optional

    :param query: Query to use to gather source documents
    :type query: QueryDSL, optional

    """

    index: list
    runtime_mappings: Optional[dict] = None
    query: Optional[QueryDSL] = None


@dataclass(repr=False, frozen=True)
class Transform(BaseResource):
    """
    Manage an Elasticsearch `Transform <https://www.elastic.co/guide/en/elasticsearch/reference/current/put-transform.html#put-transform-request-body>`__

    :param source: Transform Source
    :type source: Source

    :param dest: Destination for transform results
    :type dest: Dest

    :param id: Transform ID
    :type id: str, optional

    :param description: Transform Description
    :type description: str, optional

    :param frequency: Transform frequency
    :type frequency: str, optional

    :param pivot: Transform Pivot
    :type pivot: Pivot, optional

    :param latest: Transform Latest
    :type latest: Latest, optional

    :param sync: Transform Sync
    :type sync: Sync, optional

    :param retention_policy: Transform Retention Policy
    :type retention_policy: RetentionPolicy, optional

    :param settings: Transform settings
    :type settings: Settings, optional
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
        Get a Transform from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param transform_id: Transform id
        :type transform_id: str
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
        """
        Create a Transform in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
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

    def update(self, client, *args, **kwargs):
        """
        Update a Transform in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        return self.create(client)

    def delete(self, client, force=False, *args, **kwargs):
        """
        Delete a Transform in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
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
        """
        Stop a Transform
        """
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
        """
        Start a transform
        """
        try:
            return client.transform.start_transform(
                transform_id=self.id, timeout=timeout, *args, **kwargs
            )
        except Exception as e:
            raise e
