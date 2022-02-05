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
    index: Optional[dict] = None


@enforce_types
@dataclass(frozen=True)
class Index(BaseResource):
    name: str
    aliases: Optional[Alias] = None
    mappings: Optional[dict] = None
    settings: Optional[IndexSettings] = None

    @property
    def id(self):
        return self.name

    def asdict(self):
        d = super().asdict()
        d.pop("name")
        return d

    @classmethod
    def get(cls, client, name):
        """
        Get an index from Elasticsearch
        """
        try:
            rt = client.indices.get(index=name)
        except NotFoundError:
            return None
        ret = cls.fromdict(schemaclass=IndexSchema, body=rt)
        return ret

    def create(self, client, defer_validation=False, *args, **kwargs):
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
        try:
            return client.indices.delete(index=self.id)
        except RequestError as e:
            raise e
