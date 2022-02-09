#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Optional

from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.querydsl import QueryDSL
from nemesis.resources.elasticsearch.alias import Alias

from nemesis.schemas.elasticsearch.index import IndexSchema

from elasticsearch import RequestError, NotFoundError


@enforce_types
@dataclass(frozen=True)
class IndexSettings(BaseResource):
    """
    Manage Elasticsearch `Index Settings <https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules.html#index-modules-settings>`__

    :param index: Index settings
    :type index: dict, optional

    """

    index: Optional[dict] = None


@enforce_types
@dataclass(frozen=True)
class Index(BaseResource):
    """
    Manage an `Elasticsearch Index <https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html>`__

    :param name: Name of the index you wish to interact with.
    :type name: str

    :param aliases: Aliases for the index.
    :type aliases: Alias, optional

    :param mappings: Mapping for fields in the index.
    :type mappings: dict, optional

    :param settings: Configuration options for the index
    :type settings: IndexSettings, optional

    """

    name: str
    aliases: Optional[Alias] = None
    mappings: Optional[dict] = None
    settings: Optional[IndexSettings] = None

    @property
    def id(self):
        return self.name

    def asdict(self):
        """
        Return Index as a dictionary
        """
        d = super().asdict()
        d.pop("name")
        return d

    @classmethod
    def get(cls, client, name):
        """
        Get an index from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param name: Index name
        :type name: str

        """
        try:
            rt = client.indices.get(index=name)
        except NotFoundError:
            return None
        ret = cls.fromdict(schemaclass=IndexSchema, body=rt)
        return ret

    def create(self, client, *args, **kwargs):
        """
        Create an index in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        try:
            return client.indices.create(
                index=self.id,
                mappings=self.asdict().get("mappings"),
                settings=self.asdict().get("settings"),
                aliases=self.asdict().get("aliases"),
                *args,
                **kwargs,
            )
        except RequestError as e:
            raise e

    def delete(self, client):
        """
        Delete an index from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        try:
            return client.indices.delete(index=self.id)
        except RequestError as e:
            raise e
