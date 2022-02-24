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
    """
    Application for an Elasticsearch Role

    :param application: Application name
    :type application: str

    :param privileges: Privileges for the application
    :type privileges: list

    :param resources: Resources the application has access to
    :type resources: list
    """

    application: str
    privileges: list
    resources: list


@enforce_types
@dataclass(frozen=True)
class Index(BaseResource):
    """
    Index for an Elasticsearch Role

    :param name: index name
    :type name: str

    :param privileges: Privileges for the index
    :type privileges: list

    :param field_security: Field level security
    :type field_security: list, optional

    :param allow_restricted_indices: Allow restricted indices
    :type field_security: bool, optionl
    """

    names: list
    privileges: list
    query: Optional[QueryDSL] = None
    field_security: Optional[dict] = None
    allow_restricted_indices: Optional[bool] = None


@enforce_types
@dataclass(repr=False, frozen=True)
class Role(BaseResource):
    """
    Security Role for a Elasticsearch

    :param name: Role name
    :type name: str

    :param applications: List of :py:mod:`application`
    :type applications: list

    :param cluster: List of clusters
    :type cluster: list, optional

    :param indices: List of :py:mod:`Index`
    :type indices: list

    :param metadata: Optional Role metadata
    :type metadata: dict, optionl

    :param run_as: Optional list of users to run as for this role.
    :type run_as: list, optionl

    :param _global: Optional global setting for this role
    :type _global: bool, optional
    """

    name: str
    applications: list
    cluster: list
    indices: list
    metadata: Optional[dict] = None
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

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param name: Role name
        :type name: str
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
        """
        Create a Role in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        body = self.asdict()
        try:
            return client.security.put_role(name=self.id, body=body)
        except Exception as e:
            raise e

    def update(self, client):
        """
        Update a Role in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        return self.create(client)

    def delete(self, client):
        """
        Delete a Role in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        try:
            return client.security.delete_role(name=self.id)
        except Exception as e:
            raise e


@enforce_types
@dataclass(repr=False, frozen=True)
class RoleMapping(BaseResource):
    """
    Manage a RoleMapping in Elasticsearch

    :param name: Name of the role mapping
    :type name: str

    :param enabled: Enable or disable the role mapping.
    :type enabled: bool

    :param rules: Rules for this role mapping
    :type rules: dict

    :param roles: List of :py:mod:`Role` to associate to this role mapping.
    :type roles: list, optional

    :param role_templates: List of Role templates.
    :type role_templates: list, optional

    :param metadata: Optional metadata to associate to this role mapping
    :type metadata: dict, optional
    """

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
        Get a RoleMapping from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param pipeline_id: Ingest pipeline id
        :type pipeline_id: str
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
        """
        Create a RoleMapping in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        body = self.asdict()
        try:
            return client.security.put_role_mapping(name=self.id, body=body)
        except Exception as e:
            raise e

    def update(self, client):
        """
        Update a RoleMapping in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        return self.create(client)

    def delete(self, client):
        """
        Delete a RoleMapping in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        body = self.asdict()
        try:
            return client.security.delete_role_mapping(name=self.id)
        except Exception as e:
            raise e
