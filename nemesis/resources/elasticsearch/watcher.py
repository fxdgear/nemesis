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
    """
    Watch Trigger

    :param schedule: Schedule to trigger a watch.
    :type schedule: dict
    """

    schedule: dict


@enforce_types
@dataclass(repr=False, frozen=True)
class Body(BaseResource):
    """
    Watch Body

    :param query: Schedule to trigger a watch.
    :type query: QueryDSL

    :param size: Optional size parameter.
    :type size: int, optional

    :param sort: Sort Dictionary
    :type sort: dict, optional
    """

    query: QueryDSL
    size: Optional[int] = None
    sort: Optional[dict] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class SearchTemplate(BaseResource):
    """
    Watch Search Template

    :param id: Search template id
    :type id: str

    :param params: Search template parameters
    :type params: dict
    """

    id: str
    params: dict


@enforce_types
@dataclass(repr=False, frozen=True)
class SearchRequest(BaseResource):
    """
    Watch Search Request

    :param indices: List of indices to search.
    :type indices: list

    :param body: Watch Body
    :type body: Body

    :param template: SearchTemplate
    :type template: SearchTemplate, optional
    """

    indices: list
    body: Body
    template: Optional[SearchTemplate] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class Search(BaseResource):
    """
    Watch Search

    :param request: Watch Search Request.
    :type indices: SearchRequest

    :param extract: Optional list to extract
    :type extract: list, optional
    """

    request: SearchRequest
    extract: Optional[list] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class HttpRequest(BaseResource):
    """
    http request object

    :param scheme: http url scheme.
    :type scheme: str, optional

    :param host: Url host
    :type host: str, optional

    :param port: url port.
    :type port: str, optional

    :param url: Request URL.
    :type url: str, optional

    :param method: Request method.
    :type method: str, optional

    :param body: Request body.
    :type body: str, optional

    :param params: Request params.
    :type params: str, optional

    :param headers: Request headers.
    :type headers: str, optional

    :param auth: Request auth.
    :type auth: str, optional

    :param proxy: Request proxy.
    :type proxy: str, optional

    :param connection_timeout: Request connection timeout.
    :type connection_timeout: str, optional

    :param read_timeout: Request read timeout.
    :type read_timeout: str, optional

    :param extract: Request extract.
    :type extract: str, optional

    :param response_content_type: Request response content type.
    :type response_content_type: str, optional

    """

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
    """
    Watch HTTP object

    :param request: Http Request object
    :type request: HttpRequest
    """

    request: HttpRequest


@enforce_types
@dataclass(repr=False, frozen=True)
class Chain(BaseResource):
    """
    Watch Chain

    :param inputs: Input parameters
    :type inputs: list
    """

    inputs: list


@enforce_types
@dataclass(repr=False, frozen=True)
class Input(BaseResource):
    """Watch Input

    :param simple: Optiona dict of simple inputs
    :type simple: dict

    :param search: Optional Search input
    :type search: Search

    :param http: Optional HTTP input
    :type http: Http

    :param chain: Optional Chain input
    :type chain: Chain

    """

    simple: Optional[dict] = None
    search: Optional[Search] = None
    http: Optional[Http] = None
    chain: Optional[Chain] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class Condition(BaseResource):
    """
    Watch Condition.


    :param always: Always condition
    :type always: dict, optional

    :param never: Never Condition
    :type always: dict, optional

    :param compare: Compare Condition
    :type always: dict, optional

    :param array_compare: Array compare Condition
    :type always: dict, optional

    :param script: Script Condition
    :type always: dict, optional

    """

    always: Optional[dict] = None
    never: Optional[dict] = None
    compare: Optional[dict] = None
    array_compare: Optional[dict] = None
    script: Optional[dict] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class EmailAction(BaseResource):
    """
    Watch Email Action

    :param id: Email action id
    :type id: str

    :param account: Email account to use
    :type account: str

    :param profile: email profile to use
    :type profile: str

    :param to: List of email addresses to send too
    :type to: list

    :param cc: List of email addresses to cc
    :type cc: list

    :param bcc: List of email addresses to bcc
    :type bcc: list

    :param reply_to: Reply to address
    :type reply_to: list

    :param _from: Who the email is from
    :type _from: str

    :param subject: Email subject
    :type subject: str

    :param body: Email body
    :type body: str

    :param body_text: Email body text
    :type body_text: str

    :param body_html: email body html
    :type body_html: str

    :param priority: Priory
    :type priority: str

    :param attachments: email attachments
    :type attachments: str

    """

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
    """
    Elasticsearch Watch

    :param watch_id: watch id
    :type watch_id: str

    :param trigger:  Watch trigger
    :type trigger: Trigger

    :param input:  Watch input
    :type input: Input

    :param condition:  Watch condition
    :type condition: Condition

    :param actions:  Watch actions to perform
    :type actions: dict

    :param metadata: Optional metadata for the watch.
    :type metadata: dict, optional

    :param throttle_period: Optional throttle period
    :type throttle_period: int, optional

    :param throttle_period_in_millis: Optional throttle period in milliseconds.
    :type throttle_period_in_millis: int, optional

    """

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
        Get a Watcher from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param name: Index template name
        :type name: str
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
        """
        Create a watcher in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        try:
            return client.watcher.put_watch(id=self.id, body=self.asdict())
        except Exception as e:
            raise e

    def delete(self, client):
        """
        Delete a watcher in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        try:
            return client.watcher.delete_watch(id=self.id)
        except Exception as e:
            raise e

    def update(self, client):
        """
        Update a watcher in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        return self.create(client)
