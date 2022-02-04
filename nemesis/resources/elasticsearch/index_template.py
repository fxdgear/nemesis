#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dacite
from dataclasses import dataclass, field
from typing import Optional
from elasticsearch import NotFoundError
from nemesis.exceptions import MultipleObjectsReturned
from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.alias import Alias
from nemesis.schemas.elasticsearch.index_template import IndexTemplateSchema


@enforce_types
@dataclass(frozen=True)
class IndexSettings(BaseResource):
    index: Optional[dict] = None


@enforce_types
@dataclass(frozen=True)
class Template(BaseResource):
    settings: Optional[IndexSettings] = None
    mappings: Optional[dict] = None
    aliases: Optional[Alias] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class IndexTemplate(BaseResource):
    name: str
    index_patterns: list
    template: Template
    version: Optional[int] = None
    priority: Optional[int] = None
    composed_of: Optional[list] = None
    meta: Optional[dict] = None

    @property
    def id(self):
        return self.name

    def asdict(self):
        """
        The "name" field isn't part of the actual body sent to Elasticsearch.
        But it's nice to have on the object we are dealing with.
        """
        d = super().asdict()
        d.pop("name")
        return d

    @classmethod
    def get(cls, client, name):
        """
        Get an index template from Elasticsearch
        """
        try:
            rt = client.indices.get_index_template(name=name, flat_settings=False)
        except NotFoundError:
            return None
        data = rt["index_templates"]
        ret = []

        schema = IndexTemplateSchema()
        for item in data:
            result = schema.load(item)
            template = dacite.from_dict(data_class=cls, data=result)
            ret.append(template)
        if len(ret) > 1:
            raise MultipleObjectsReturned
        else:
            return ret[0]

    def create(self, client):
        try:
            return client.indices.put_index_template(
                name=self.name, body=self.asdict(), create=True
            )
        except Exception as e:
            raise e

    def update(self, client):
        try:
            return client.indices.put_index_template(
                name=self.name, body=self.asdict(), create=False
            )
        except Exception as e:
            raise e

    def delete(self, client):
        try:
            return client.indices.delete_index_template(name=self.name)
        except Exception as e:
            raise e
