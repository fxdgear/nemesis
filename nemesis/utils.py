#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from deepdiff.helper import NotPresent

ADD = "[add]+[/]"
REMOVE = "[remove]-[/]"
CHANGE = "[change]~[/]"


class Diff:
    local_resource = None
    remote_resource = None
    status = "update"

    def __init__(self, local_resource, remote_resource):
        self.local_resource = local_resource
        self.remote_resource = remote_resource
        self.deltas = []
        self.do_diff()

    def _values_changed(self, diff):
        self.status = "update"
        for item in diff:
            path = item.path().replace("root", "")
            self.deltas.append(
                {
                    "path": path,
                    "long": f"{ADD} {json.dumps(item.t1, indent=2)}\n{REMOVE} {json.dumps(item.t2, indent=2)}",
                    "short": f"{CHANGE} {path}",
                }
            )

    def _dictionary_item_added(self, diff):
        self.status = "update"
        for item in diff:
            path = item.path().replace("root", "")
            if isinstance(item.t1, NotPresent):
                # This scenario means the object was edited in Kibana and the resource defined
                # in nemesis doesn't match what's remote.
                # We have an item that doesn't exist locally, yet exists remotely.
                # This can happen when a logstash pipeline is edited in Kibana, and changes the `metadata`.
                self.deltas.append(
                    {
                        "path": path,
                        "long": f"{ADD} {json.dumps(item.t2, indent=2)}",
                        "short": f"{ADD} {path}",
                    }
                )
            else:
                self.deltas.append(
                    {
                        "path": path,
                        "long": f"{ADD} {json.dumps(item.t2, indent=2)}",
                        "short": f"{ADD} {path}",
                    }
                )

    def _dictionary_item_removed(self, diff):
        if self.remote_resource is None:
            self.status = "create"

        for item in diff:
            path = item.path().replace("root", "")
            if isinstance(item.t2, NotPresent):
                # If the remote_resource is None, and item.t2 is NotPresent
                # This means the remote object does Not exist, and we are adding
                # the full resource.
                self.deltas.append(
                    {
                        "path": path,
                        "long": f"{ADD} {json.dumps(item.t1, indent=2)}",
                        "short": f"{ADD} {path}",
                    }
                )
            else:
                self.deltas.append(
                    {
                        "path": path,
                        "long": f"{REMOVE} {json.dumps(item.t1, indent=2)}",
                        "short": f"{REMOVE} {path}",
                    }
                )

    def _iterable_item_added(self, diff):
        self.status = "update"
        for item in diff:
            path = item.path().replace("root", "")
            self.deltas.append(
                {
                    "path": path,
                    "long": f"{ADD} {json.dumps(item.t2, indent=2)}",
                    "short": f"{ADD} {path}",
                }
            )

    def _iterable_item_removed(self, diff):
        self.status = "update"
        for item in diff:
            path = item.path().replace("root", "")
            self.deltas.append(
                {
                    "path": path,
                    "long": f"{REMOVE} {json.dumps(item.t1, indent=2)}",
                    "short": f"{REMOVE} {path}",
                }
            )

    def do_diff(self):
        deepdiff = self.local_resource.diff(self.remote_resource)
        if not deepdiff:
            self.status = "unchanged"
        for reason, diff in deepdiff.items():
            if reason == "values_changed":
                self._values_changed(diff)
            elif reason == "dictionary_item_added":
                self._dictionary_item_added(diff)
            elif reason == "dictionary_item_removed":
                self._dictionary_item_removed(diff)
            elif reason == "iterable_item_removed":
                self._iterable_item_removed(diff)
            elif reason == "iterable_item_added":
                self._iterable_item_added(diff)

