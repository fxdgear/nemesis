#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import importlib.resources
import click

from nemesis import Nemesis


def load_nemesis_module():
    path = os.getcwd()
    if not os.path.exists(os.path.join(path, "__nemesis__.py")):
        return False
    sys.path.insert(0, path)
    return True


@click.group(chain=True)
def cli():
    """
    Nemesis CLI
    """
    pass


@cli.command("new", help="Create a new nemesis deployment")
def new():
    filename = "__nemesis__.py"
    text = importlib.resources.read_text("nemesis.templates", "__nemesis__.py.tmpl")
    click.echo("Create a new nemesis deployment")
    if not load_nemesis_module():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write(text)
    else:
        click.echo("Nemesis module already exists.")


@cli.command("preview", help="Preview the resources to deployed")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="More detailed preview of resources to be deployed.",
)
def preview(verbose):
    if not load_nemesis_module():
        print("No nemesis deployments found.")
        sys.exit()
    try:
        from __nemesis__ import n
    except ImportError as e:
        print("Unable to load nemesis launcher")
        raise
    n.preview(verbose)


@cli.command("launch", help="Deploy resources to Elasticsearch")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="More detailed preview of resources to be deployed.",
)
@click.option("--autoyes", "-y", is_flag=True, help="Don't prompt before launching")
@click.option("--no-preview", "-p", is_flag=True, help="Don't preview before launching")
def launch(verbose, autoyes, no_preview):
    if not load_nemesis_module():
        print("No nemesis deployments found.")
        sys.exit()
    try:
        from __nemesis__ import n
    except ImportError:
        print("Unable to load nemesis launcher")

    if not no_preview:
        n.preview(verbose)

    if not autoyes:
        confirm = input("Do you want to continue? [y/n default: n]")
    else:
        confirm = "y"

    if confirm.lower() == "y":
        n.launch(verbose)
