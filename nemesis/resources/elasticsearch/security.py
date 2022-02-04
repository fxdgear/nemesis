#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dacite
from marshmallow.exceptions import ValidationError
from dataclasses import dataclass, field
from typing import Optional, Union
from nemesis.schemas.elasticsearch.security import RoleSchema, RoleMappingSchema
from nemesis.resources import enforce_types, BaseResource
from nemesis.resources.elasticsearch.querydsl import QueryDSL


@enforce_types
@dataclass(frozen=True)
class Application(BaseResource):
    application: str
    privileges: list
    resources: list


@enforce_types
@dataclass(frozen=True)
class Index(BaseResource):
    names: list
    privileges: list
    query: Optional[QueryDSL] = None
    field_security: Optional[dict] = None
    allow_restricted_indices: Optional[bool] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class Role(BaseResource):
    name: str
    applications: list[Application]
    cluster: list
    indices: list[Index]
    metadata: dict
    run_as: Optional[list] = None
    _global: Optional[dict] = None

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
        Get a role from Elasticsearch
        """
        rt = client.security.get_role(name=name)
        schema = RoleSchema()
        try:
            result = schema.load(rt)
        except ValidationError as e:
            raise e
        role = dacite.from_dict(data_class=cls, data=result)
        return role

    def create(self, client):
        body = self.asdict()
        try:
            return client.security.put_role(name=self.id, body=body)
        except Exception as e:
            raise e

    def update(self, client):
        return self.create(client)

    def delete(self, client):
        try:
            return client.security.delete_role(name=self.id)
        except Exception as e:
            raise e


@enforce_types
@dataclass(repr=False, frozen=True)
class RoleMapping(BaseResource):
    name: str
    enabled: bool
    rules: dict
    roles: Optional[list] = None
    role_templates: Optional[list] = None
    metadata: Optional[dict] = None

    def asdict(self):
        """
        The "name" field isn't part of the actual body sent to Elasticsearch.
        But it's nice to have on the object we are dealing with.
        """
        d = super().asdict()
        d.pop("name")
        return d

    @property
    def id(self):
        return self.name

    def __post_init__(self):
        if self.roles is None and self.role_templates is None:
            raise TypeError(
                "Value needed for one of either `roles` or `role_templates`."
            )

    @classmethod
    def get(cls, client, name):
        """
        Get a role from Elasticsearch
        """
        rt = client.security.get_role_mapping(name=name)
        schema = RoleMappingSchema()
        try:
            result = schema.load(rt)
        except ValidationError as e:
            raise e
        role = dacite.from_dict(data_class=cls, data=result)
        return role

    def create(self, client):
        body = self.asdict()
        try:
            return client.security.put_role_mapping(name=self.id, body=body)
        except Exception as e:
            raise e

    def update(self, client):
        return self.create(client)

    def delete(self, client):
        body = self.asdict()
        try:
            return client.security.delete_role_mapping(name=self.id)
        except Exception as e:
            raise e
