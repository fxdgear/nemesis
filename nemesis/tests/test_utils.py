#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import MagicMock
from deepdiff import DeepDiff

from nemesis.utils import Diff
from nemesis.resources.elasticsearch.index_template import IndexTemplate, Template


def test_iterable_item_added():
    t1 = IndexTemplate(
        name="name",
        index_patterns=[
            "a",
        ],
        template=Template(),
    )
    t2 = IndexTemplate(
        name="name",
        index_patterns=["a", "b"],
        template=Template(),
    )
    diff = Diff(t1, t2)
    assert len(diff.deltas) == 1
    delta = diff.deltas[0]
    assert delta["long"] == '[add]+[/] "b"'
    assert delta["short"] == "[add]+[/] ['index_patterns'][1]"
    assert delta["path"] == "['index_patterns'][1]"


def test_iterable_item_added_remote_dne():
    t1 = IndexTemplate(
        name="name",
        index_patterns=[
            "a",
        ],
        template=Template(),
    )
    diff = Diff(t1, None)
    assert len(diff.deltas) == 2

    delta1 = diff.deltas[0]
    delta2 = diff.deltas[1]
    assert delta1["long"] == '[add]+[/] [\n  "a"\n]'
    assert delta1["short"] == "[add]+[/] ['index_patterns']"
    assert delta1["path"] == "['index_patterns']"
    assert delta2["long"] == "[add]+[/] {}"
    assert delta2["short"] == "[add]+[/] ['template']"
    assert delta2["path"] == "['template']"


def test_iterable_item_removed():
    t1 = IndexTemplate(
        name="name",
        index_patterns=["a", "b"],
        template=Template(),
    )
    t2 = IndexTemplate(
        name="name",
        index_patterns=[
            "a",
        ],
        template=Template(),
    )
    diff = Diff(t1, t2)
    assert len(diff.deltas) == 1
    delta = diff.deltas[0]
    assert delta["long"] == '[remove]-[/] "b"'
    assert delta["short"] == "[remove]-[/] ['index_patterns'][1]"
    assert delta["path"] == "['index_patterns'][1]"


def test_dictionary_item_added():
    t1 = Template(
        mappings={"a": {"b": "c"}},
    )
    t2 = Template(
        mappings={"a": {"b": "c", "d": "e"}},
    )
    diff = Diff(t1, t2)
    assert len(diff.deltas) == 1
    delta = diff.deltas[0]
    assert delta["long"] == '[add]+[/] "e"'
    assert delta["short"] == "[add]+[/] ['mappings']['a']['d']"
    assert delta["path"] == "['mappings']['a']['d']"


def test_dictionary_item_added_remote_dne():
    t1 = Template(
        mappings={"a": {"b": "c"}},
    )
    diff = Diff(t1, None)
    assert len(diff.deltas) == 1
    delta = diff.deltas[0]
    assert delta["long"] == '[add]+[/] {\n  "a": {\n    "b": "c"\n  }\n}'
    assert delta["short"] == "[add]+[/] ['mappings']"
    assert delta["path"] == "['mappings']"


def test_values_changed():
    t1 = Template(
        mappings={"a": {"b": "c"}},
    )
    t2 = Template(
        mappings={"a": {"b": "d"}},
    )
    diff = Diff(t1, t2)
    assert len(diff.deltas) == 1
    delta = diff.deltas[0]
    assert delta["long"] == '[add]+[/] "c"\n[remove]-[/] "d"'
    assert delta["short"] == "[change]~[/] ['mappings']['a']['b']"
    assert delta["path"] == "['mappings']['a']['b']"

