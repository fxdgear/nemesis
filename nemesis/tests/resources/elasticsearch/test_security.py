#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from dataclasses import FrozenInstanceError
from nemesis.resources.elasticsearch.security import (
    Role,
    RoleMapping,
    Index,
    Application,
)
from nemesis.resources.elasticsearch.querydsl import QueryDSL
from elasticsearch import Elasticsearch, RequestError

from nemesis.tests import es_client, nemesis_client


@pytest.fixture
def role():
    return Role(
        name="test-role",
        cluster=["all"],
        indices=[
            Index(
                names=["index1", "index2"],
                privileges=["all"],
                field_security={"grant": ["title", "body"]},
                query=QueryDSL(match={"title": "foo"}),
            )
        ],
        applications=[
            Application(
                application="myapp", privileges=["admin", "read"], resources=["*"]
            )
        ],
        run_as=["other_user"],
        metadata={"version": "1"},
    )


@pytest.fixture
def role_mapping(role):
    return RoleMapping(
        name="test-role-mapping",
        enabled=True,
        rules={"field": {"username": "*"}},
        roles=[role.name],
    )


def test_asdict(role, role_mapping):
    """
    asdict method pop's the `name` field from the object to match
    how it would be sent or received from Elasticsearch
    """
    assert role.asdict() == {
        "applications": [
            {
                "application": "myapp",
                "privileges": ["admin", "read"],
                "resources": ["*"],
            }
        ],
        "cluster": ["all"],
        "indices": [
            {
                "names": ["index1", "index2"],
                "privileges": ["all"],
                "query": {"match": {"title": "foo"}},
                "field_security": {"grant": ["title", "body"]},
            }
        ],
        "metadata": {"version": "1"},
        "run_as": ["other_user"],
    }

    assert role_mapping.asdict() == {
        "enabled": True,
        "rules": {"field": {"username": "*"}},
        "roles": [
            "test-role",
        ],
    }


def test_frozen_object(role, role_mapping):
    with pytest.raises(FrozenInstanceError):
        role.cluster = ["raise-error"]

    with pytest.raises(FrozenInstanceError):
        role_mapping.enabled = False


def test_id(role, role_mapping):
    assert role.id == "test-role"
    assert role_mapping.id == "test-role-mapping"


def test_create_update_delete(role, role_mapping, es_client):
    result = role.create(es_client)
    assert result == {"role": {"created": True}}

    result = role_mapping.create(es_client)
    assert result == {"role_mapping": {"created": True}}

    # test what happens when we call create a 2nd time
    result = role.create(es_client)
    assert result == {"role": {"created": False}}

    result = role_mapping.create(es_client)
    assert result == {"role_mapping": {"created": False}}

    result = role.update(es_client)
    assert result == {"role": {"created": False}}

    result = role_mapping.update(es_client)
    assert result == {"role_mapping": {"created": False}}

    result = role.delete(es_client)
    assert result == {"found": True}

    result = role_mapping.delete(es_client)
    assert result == {"found": True}
