#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dacite
from marshmallow.exceptions import ValidationError
from dataclasses import dataclass, field
from typing import Optional, Union
from nemesis.resources import enforce_types, BaseResource
from nemesis.schemas.elasticsearch.watcher import WatchSchema
from nemesis.resources.elasticsearch.querydsl import QueryDSL
from elasticsearch import NotFoundError


@enforce_types
@dataclass(repr=False, frozen=True)
class Trigger(BaseResource):
    schedule: dict


@enforce_types
@dataclass(repr=False, frozen=True)
class Body(BaseResource):
    query: QueryDSL
    size: Optional[int] = None
    sort: Optional[dict] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class SearchTemplate(BaseResource):
    id: str
    params: dict


@enforce_types
@dataclass(repr=False, frozen=True)
class SearchRequest(BaseResource):
    indices: list
    body: Body
    template: Optional[SearchTemplate] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class Search(BaseResource):
    request: SearchRequest
    extract: Optional[list] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class HttpRequest(BaseResource):
    scheme: Optional[str] = "http"
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    url: Optional[str] = None
    method: Optional[str] = "get"
    body: Optional[str] = None
    params: Optional[dict] = None
    headers: Optional[dict] = None
    auth: Optional[dict] = None
    proxy: Optional[dict] = None
    connection_timeout: Optional[str] = "10s"
    read_timeout: Optional[str] = "10s"
    extract: Optional[list] = None
    response_content_type: Optional[str] = "json"

    def __post_init__(self):
        if self.url is not None and any(
            elem is not None
            for elem in [self.scheme, self.host, self.port, self.params]
        ):
            raise TypeError(
                "If using `url` can not use any of [`scheme`, `host`, `port`, `params`]"
            )


@enforce_types
@dataclass(repr=False, frozen=True)
class Http(BaseResource):
    request: HttpRequest


@enforce_types
@dataclass(repr=False, frozen=True)
class Chain(BaseResource):
    inputs: list


@enforce_types
@dataclass(repr=False, frozen=True)
class Input(BaseResource):
    simple: Optional[dict] = None
    search: Optional[Search] = None
    http: Optional[Http] = None
    chain: Optional[Chain] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class Condition(BaseResource):
    always: Optional[dict] = None
    never: Optional[dict] = None
    compare: Optional[dict] = None
    array_compare: Optional[dict] = None
    script: Optional[dict] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class EmailAction(BaseResource):
    id: str
    account: str
    profile: str
    to: list
    cc: list
    bcc: list
    reply_to: list
    _from: str
    subject: str
    body: str
    body_text: str
    body_html: str
    priority: str
    attachments: str


@enforce_types
@dataclass(repr=False, frozen=True)
class Watch(BaseResource):
    watch_id: str
    trigger: Trigger
    input: Input
    condition: Condition
    actions: dict
    metadata: Optional[dict] = None
    throttle_period: Optional[int] = None
    throttle_period_in_millis: Optional[int] = None

    @property
    def id(self):
        return self.watch_id

    def asdict(self):
        d = super().asdict()
        d.pop("watch_id")
        return d

    @classmethod
    def get(cls, client, watch_id):
        """
        Get a watch from Elasticsearch
        """
        try:
            rt = client.watcher.get_watch(id=watch_id)
        except NotFoundError:
            return None
        schema = WatchSchema()
        try:
            result = schema.load(rt)
        except ValidationError as e:
            raise e
        except TypeError as e:
            raise e
        role = dacite.from_dict(data_class=cls, data=result)
        return role

    def create(self, client):
        try:
            return client.watcher.put_watch(id=self.id, body=self.asdict())
        except Exception as e:
            raise e

    def delete(self, client):
        try:
            return client.watcher.delete_watch(id=self.id)
        except Exception as e:
            raise e

    def update(self, client):
        return self.create(client)
