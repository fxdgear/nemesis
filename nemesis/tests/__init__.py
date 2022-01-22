#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os

from nemesis import Nemesis

TEST_USERNAME = os.environ.get('TEST_USERNAME', 'elastic')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD', 'changeme')
TEST_HOST = os.environ.get('TEST_HOST', 'http://localhost:9200')


def get_client(username=TEST_USERNAME, password=TEST_PASSWORD, es_host=TEST_HOST):
    return Nemesis(username=username, password=password, es_host=es_host)

@pytest.fixture
def nemesis_client():
    return get_client()

@pytest.fixture
def es_client():
    n = get_client()
    return n.client
