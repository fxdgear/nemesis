#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from deepdiff.helper import NotPresent


class Diff:
    local_resource = None
    remote_resource = None
    status = "update"

    def __init__(self, local_resource, remote_resource):
        self.local_resource = local_resource
        self.remote_resource = remote_resource
        self.deltas = []
        self.do_diff()

    def do_diff(self):

        deepdiff = self.local_resource.diff(self.remote_resource)
        if not deepdiff:
            self.status = "unchanged"
        for reason, diff in deepdiff.items():
            if reason == "values_changed":
                self.status = "update"
                for item in diff:
                    path = item.path().replace("root", "")
                    self.deltas.append(
                        {
                            "path": path,
                            "long": f"[add]+[/add] {json.dumps(item.t1, indent=2)}\n[remove]-[/remove] {json.dumps(item.t2, indent=2)}",
                            "short": f"[change]~[/] {path}",
                        }
                    )

            elif reason == "dictionary_item_added":
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
                                "long": f"[remove]-[/remove] {item.t2}",
                                "short": f"[remove]-[/] {path}",
                            }
                        )
                    else:
                        self.deltas.append(
                            {
                                "path": path,
                                "long": item.t1,
                                "short": f"[remove]-[/] {path}",
                            }
                        )

            elif reason == "dictionary_item_removed":
                if self.remote_resource is None:
                    self.status = "create"

                for item in diff:
                    path = item.path().replace("root", "")
                    self.deltas.append(
                        {
                            "path": path,
                            "long": f"[add]+[/add] {json.dumps(item.t1, indent=2)}",
                            "short": f"[add]+[/] {path}",
                        }
                    )

            elif reason == "iterable_item_removed":
                self.status = "update"
                for item in diff:
                    path = item.path().replace("root", "")
                    self.deltas.append(
                        {
                            "path": path,
                            "long": f"[add]+[/add] {json.dumps(item.t1, indent=2)}",
                            "short": f"[add]+[/] {path}",
                        }
                    )

            elif reason == "iterable_item_added":
                self.status = "update"
                for item in diff:
                    path = item.path().replace("root", str(self.local_resource))
                    self.deltas.append(
                        {
                            "path": path,
                            "long": f"[remove]+[/remove] {json.dumps(item.t2, indent=2)}",
                            "short": f"[remove]+[/] {path}",
                        }
                    )
                    self.deltas.append(f"[remove]-[/] {path}")
