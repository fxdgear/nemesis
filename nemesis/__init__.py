#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
from rich.table import Table
import requests
from elasticsearch import Elasticsearch

from nemesis.console import console
from nemesis.resources import ELASTICSEARCH
from nemesis.utils import Diff


class Nemesis:
    """
    Nemesis is our main class for which the whole project revolves around.

    :param username: username to Auth against Elasticsearch
    :type username: str

    :param password: password to Auth against Elasticsearch
    :type password: str

    :param es_host: URL where to Auth against Elasticsearch
    :type es_host: str, optional

    :param cloud_id: Cloud ID where to Auth against Elasticsearch
    :type cloud_id: str, optional
    """

    def __init__(self, username, password, es_host=None, cloud_id=None):
        if cloud_id is not None:
            self.client = Elasticsearch(
                cloud_id=cloud_id, http_auth=(username, password)
            )
        else:
            self.client = Elasticsearch(es_host, http_auth=(username, password))
        self.resources = []
        self.diffs = []

    def get_client_for(self, resource):
        """
        For a given resource, return the right python client.

        :param resource: Nemesis resource
        :type resource: :mod:`nemesis.resources`
        """
        if resource.stack_type == ELASTICSEARCH:
            return self.client

    def register(self, resource, force=False, pre_deploy=None, post_deploy=None):
        """
        Register a resource with Nemesis to be deployed to Elasticsearch.
        """
        self.resources.append(
            {
                "resource": resource,
                "remote_resource": resource.get(
                    self.get_client_for(resource), resource.id
                ),
                "force": force,
                "pre_deploy": pre_deploy,
                "post_deploy": post_deploy,
            }
        )

    def preview(self, verbose=False):
        """
        Preview a resource vs the existing resource in Elasticsearch.
        """
        if verbose:
            self._verbose_preview()
        else:
            self._preview()

    def _verbose_preview(self):
        """
        Verbose preview the remote resource.
        """
        for item in self.resources:
            resource = item["resource"]
            remote_resource = item["remote_resource"]
            self.diffs.append(Diff(resource, remote_resource))

        min_width = max([len(str(x.local_resource)) for x in self.diffs]) + 10

        for diff in self.diffs:
            console.rule()
            table = Table(
                title=f"Preview [resource]{diff.local_resource}",
                min_width=min_width,
            )
            table.add_column("Field", justify="left", no_wrap=True)
            table.add_column("Value", justify="left", no_wrap=False)
            for delta in diff.deltas:
                table.add_row(delta["path"], delta["long"])
            console.print(table)

        created = len([x for x in self.diffs if x.status == "create"])
        updated = len([x for x in self.diffs if x.status == "update"])
        unchanged = len([x for x in self.diffs if x.status == "unchanged"])
        console.print("\nResources:")
        if created > 0:
            console.print(f"\tCreating: {created}")
        if updated > 0:
            console.print(f"\tUpdating: {updated}")
        if unchanged > 0:
            console.print(f"\tUnchanged: {unchanged}")

    def _preview(self):
        """
        Terse diff the remote resource.
        """
        table = Table(title="Preview resources to be deployed", show_lines=True)
        table.add_column("Resource", justify="left", no_wrap=True)
        table.add_column("Name", justify="left", no_wrap=True)
        table.add_column("Action", justify="center", no_wrap=True)
        table.add_column("Diff", justify="right", no_wrap=False)
        for item in self.resources:
            resource = item["resource"]
            remote_resource = item["remote_resource"]
            self.diffs.append(Diff(resource, remote_resource))

        for diff in self.diffs:
            local_resource = diff.local_resource
            table.add_row(
                type(local_resource).__name__,
                local_resource.id,
                diff.status,
                "\n".join([x["short"] for x in diff.deltas]),
            )

        created = len([x for x in self.diffs if x.status == "create"])
        updated = len([x for x in self.diffs if x.status == "update"])
        unchanged = len([x for x in self.diffs if x.status == "unchanged"])
        console.print(table)
        console.print("\nResources:")
        if created > 0:
            console.print(f"\tCreating: {created}")
        if updated > 0:
            console.print(f"\tUpdating: {updated}")
        if unchanged > 0:
            console.print(f"\tUnchanged: {unchanged}")

    def _no_change(self, item):
        """
        Console print "no change"
        """
        resource = item["resource"]
        console.print()
        console.rule(f"[resource]{resource}", align="left")
        console.print(
            f"[bold white]No changes detected for [resource]{resource}[/]. Skipping."
        )

    def _pre_deploy(self, resource, function):
        """Method to call the pre-deploy function registered with a resource."""
        if function is None:
            return
        else:
            console.print()
            console.print(
                f"[bold white]Running pre-deploy function [function]`{function.__name__}`[/]"
            )
            if function(self.client, resource) is False:
                console.print(
                    f"[error]Failed pre_deploy step [function]`{function.__name__}`[/]"
                )
                console.print("[error]Quitting...")
                sys.exit()

    def _post_deploy(self, resource, function):
        """Method to call the pos-deploy function registered with a resource."""
        if function is None:
            return
        else:
            console.print()
            console.print(
                f"[bold white]Running post-deploy function [function]`{function.__name__}`[/]"
            )
            if function(self.client, resource) is False:
                console.print(
                    f"[error]Failed post_deploy step [function]`{function.__name__}`[/]"
                )
                console.print("[error]Quitting...")
                sys.exit()

    def _force_deploy(self, item):
        """
        Force deploy a resource if specified to force deploy it.
        """
        resource = item["resource"]
        force = item["force"]
        pre_deploy = item["pre_deploy"]
        post_deploy = item["post_deploy"]
        console.print()
        console.rule(f"[resource]{resource}", align="left")
        console.print(
            f"[bold white]No changes detected for [resource]{resource}[/]. But [add]force[/] applied, so deploying."
        )
        self._pre_deploy(resource, pre_deploy)
        resource.update(self.get_client_for(resource))
        self._post_deploy(resource, post_deploy)

    def _deploy_update(self, item):
        """
        Deploy an update (as opposed to a create of a new resource).
        """
        resource = item["resource"]
        force = item["force"]
        pre_deploy = item["pre_deploy"]
        post_deploy = item["post_deploy"]
        console.print()
        console.rule(f"[resource]{resource}", align="left")
        console.print(f"[bold white]Updating resource: [resource]{resource}[/]")
        self._pre_deploy(resource, pre_deploy)
        resource.update(self.get_client_for(resource))
        self._post_deploy(resource, post_deploy)

    def _deploy_create(self, item):
        """
        Deploy and create a new object
        """
        resource = item["resource"]
        force = item["force"]
        pre_deploy = item["pre_deploy"]
        post_deploy = item["post_deploy"]
        console.print()
        console.rule(f"[resource]{resource}", align="left")
        console.print(f"[bold white]Creating resource: [resource]{resource}[/]")
        self._pre_deploy(resource, pre_deploy)
        resource.create(self.get_client_for(resource))
        self._post_deploy(resource, post_deploy)

    def launch(self, verbose=False):
        """
        Method to deploy resources to Elasticsearch.
        """
        console.print()
        console.rule()
        console.rule(f"Preparing to deploy {len(self.resources)} resources...")
        console.rule()
        for item in self.resources:
            resource = item["resource"]
            remote_resource = item["remote_resource"]
            force = item["force"]
            diff = next(
                (x for x in self.diffs if x.local_resource.id == resource.id), None
            )

            if not diff and not force:
                self._no_change(item)
            if not diff and force:
                self._force_deploy(item)
            if diff and remote_resource is not None:
                self._deploy_update(item)
            if diff and remote_resource is None:
                self._deploy_create(item)

        console.rule()
        console.rule(f"Completed deploying {len(self.resources)} resources.")
        console.rule()
