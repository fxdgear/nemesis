# Nemesis ![tests-badge](https://github.com/fxdgear/nemesis/actions/workflows/python-app.yml/badge.svg)

Nemesis is a python library to manage Elasticsearch resources as code. Nemesis operates
a lot more like Pulumi than terraform. Each resource that nemesis supports is an actual
python object which can be used like any other python object.

Elasticsearch resources can be crafted as Python objects.
Elasticsearch resources can be fetched from the Elasticsearch cluster and diffed against local versions.
Deployments can happen if a remote resource doesn't exist.
Deployments can happen if a local_resource is registered with force=True, to force updating of the
resource even if it hasn't changed.

Creating new resources is not trivial at this point in time.
It's difficult because, to create the resource you first need to define the dataclass and all the attributes on that class.
Next you would need to define the Schema for that resource, then you would need to define all the CRUD method for that resource.
There's no automated way to do this. But would be nice to create a code generator to scan the Elasticsearch repo and pull out the various resources and their types so they can be created in Nemesis.

Pull requests for new resources added to nemesis would be greatly appriciated!

## Getting started.

### Installation
First to get started you must install `nemesis`:

```
pip install nemesis
```

### Creating your first nemesis project

First create the directory you want to put your nemesis project into:

```
$ mkdir my_first_project
$ cd my_first_project
$ nemesis new
```

### The __nemesis__.py file

After you run the `nemesis new` command a newly created __nemesis__.py file will exist. This file has some example code in it to help you get started.

1. instantiate the `Nemesis` object as the variable `n`.
2. using the `nemesis.resources.elasticsearch.*` modules create your ES resources
3. `register` those resources with the `Nemesis` client. `n.register(my_resource_name)`

### Help

Running the `--help` flag will give you help on any command or subcommand.

```
> nemesis --help
Usage: nemesis [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

  Nemesis CLI

Options:
  --help  Show this message and exit.

Commands:
  launch   Deploy resources to Elasticsearch
  new      Create a new nemesis deployment
  preview  Preview the resources to deployed
```


### Preview

Run `nemesis preview` to see what will be deployed to Elasticsearch.

This will render a diff to tell you what's going to be created or changed.

### Launch

Run `nemesis launch` to deploy your changes.

This will actually ship your resources to Elasticsearch

---

# Additional features

## Pre/Post deploy hooks.
nemesis supports pre and post deploy hooks. This is useful in various situations:

1. You are creating an ingest pipeline and you want to run some tests to ensure your pipeline works before the pipeline is deployed.
You can write a function to call `resource.simulate` on  your pipeline resource.
2. You have a transform you want to "reset". You can define a "predeploy" function to "stop" the current transform,
  delete the current dest index, and then recreate the dest index. then define a "postdeploy" function which will start the transform
3. Watchers can be "simulated" using the "execute" api. This unfortunatly only works on watchers that exist already, but you can deploy the watcher and then write a post-deploy
test that will ensure your watcher works as expected.
4. Your imagination is the limit on things you might want to do before and/or after something has been deployed

---

# Diffing elasticsearch resources

Nemesis supports deep diffing of resources with a succinct mode and verbose mode.

Example of a "succinct" diff:

```
> nemesis launch -y
Hello Nemesis!
                             Preview resources to be deployed
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Resource         ┃ Name                             ┃  Action   ┃                 Diff ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ IndexTemplate    │ index_template_billing_aggregate │  create   │ + ['index_patterns'] │
│                  │                                  │           │       + ['template'] │
│                  │                                  │           │        + ['version'] │
├──────────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ IngestPipeline   │ total_cost                       │  create   │             + ['id'] │
│                  │                                  │           │     + ['processors'] │
│                  │                                  │           │    + ['description'] │
│                  │                                  │           │        + ['version'] │
├──────────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ Transform        │ total_cost_2021_12               │  create   │         + ['source'] │
│                  │                                  │           │           + ['dest'] │
│                  │                                  │           │             + ['id'] │
│                  │                                  │           │          + ['pivot'] │
│                  │                                  │           │    + ['description'] │
│                  │                                  │           │      + 'frequency'] │
├──────────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ LogstashPipeline │ test_logstash_pipeline           │  update   │  ~ ['last_modified'] │
├──────────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ Role             │ test-role                        │ unchanged │                      │
├──────────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ RoleMapping      │ test_role_mapping                │ unchanged │                      │
├──────────────────┼──────────────────────────────────┼───────────┼──────────────────────┤
│ Watch            │ test-watch                       │ unchanged │                      │
└──────────────────┴──────────────────────────────────┴───────────┴──────────────────────┘

Resources:
        Creating: 3
        Updating: 1
        Unchanged: 3
```

And an example of a verbose diff:
```
> nemesis launch -v
Hello Nemesis!
────────────────────────────────────────────────────────────────────────────────────────────────────────
 Preview IndexTemplate(index_template_billing_aggregate)
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field               ┃ Value                           ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ['index_patterns']  │ + [                             │
│                     │   "billing_aggregate_*"         │
│                     │ ]                               │
│ ['template']        │ + {                             │
│                     │   "settings": {                 │
│                     │     "index": {                  │
│                     │       "number_of_shards": "1",  │
│                     │       "number_of_replicas": "1" │
│                     │     }                           │
│                     │   },                            │
│                     │   "mappings": {                 │
│                     │     "_source": {                │
│                     │       "enabled": true           │
│                     │     },                          │
│                     │     "properties": {             │
│                     │       "@timestamp": {           │
│                     │         "type": "date"          │
│                     │       },                        │
│                     │       "@version": {             │
│                     │         "type": "text"          │
│                     │       },                        │
│                     │       "cloud_provider": {       │
│                     │         "type": "keyword"       │
│                     │       },                        │
│                     │       "sum_total": {            │
│                     │         "type": "float"         │
│                     │       },                        │
│                     │       "team_name": {            │
│                     │         "type": "keyword"       │
│                     │       }                         │
│                     │     }                           │
│                     │   }                             │
│                     │ }                               │
│ ['version']         │ + 3                             │
└─────────────────────┴─────────────────────────────────┘
```
