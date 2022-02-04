#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Optional

from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.querydsl import QueryDSL
from nemesis.resources.elasticsearch.alias import Alias

from elasticsearch import RequestError


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

    def create(self, client, defer_validation=False, *args, **kwargs):
        print(f"Creating {self}.")
        try:
            return client.indices.create(
                index=self.id,
                body=self.asdict(),
                *args,
                **kwargs,
            )
        except RequestError as e:
            raise e

    def delete(self, client):
        try:
            return client.indices.delete(self.id)
        except RequestError as e:
            raise e