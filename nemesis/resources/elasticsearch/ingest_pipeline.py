#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dacite
from elasticsearch import NotFoundError
from dataclasses import dataclass, field
from typing import Optional
from nemesis.schemas.elasticsearch.ingest_pipeline import IngestPipelineSchema
from nemesis.resources import enforce_types, BaseResource


@enforce_types
@dataclass(repr=False, frozen=True)
class IngestPipeline(BaseResource):
    """
    Manage an `Ingest Pipeline <https://www.elastic.co/guide/en/elasticsearch/reference/master/put-pipeline-api.html>`__

    :param id: ID of an ingest pipeline
    :type id: str

    :param processors: List of `Processors <https://www.elastic.co/guide/en/elasticsearch/reference/master/processors.html>`__ for an ingest pipeline.
    :type processors: list

    :param description: Description of the Ingest Pipeline.
    :type description: str, optional

    :param on_failure: List of `Processors <https://www.elastic.co/guide/en/elasticsearch/reference/master/processors.html>`__ in case of failure.
    :type on_failure: list

    :param version: Version number of the ingest pipeline
    :type version: str, optional

    :param _meta: Optional metadata about the ingest pipeline
    :type _meta: dict, optional

    """

    id: str
    processors: list
    description: Optional[str] = None
    on_failure: Optional[list] = None
    version: Optional[int] = None
    _meta: Optional[dict] = None

    @classmethod
    def get(cls, client, pipeline_id):
        """
        Get an ingest pipeline from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param pipeline_id: Ingest pipeline id
        :type pipeline_id: str
        """
        try:
            pipeline = client.ingest.get_pipeline(id=pipeline_id)
        except NotFoundError:
            return None
        schema = IngestPipelineSchema()
        result = schema.load(pipeline)
        pipeline = dacite.from_dict(data_class=cls, data=result)
        return pipeline

    def create(self, client):
        """
        Create an ingest pipeline in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        body = self.asdict()
        body.pop("id")
        return client.ingest.put_pipeline(id=self.id, body=body)

    def delete(self, client):
        """
        Delete an ingestpipeline from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`
        """
        try:
            return client.ingest.delete_pipeline(id=self.id)
        except Exception as e:
            raise e

    def update(self, client):
        """
        Update an ingest pipeline in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        return self.create(client)

    def simulate(self, client, docs):
        """
        Simulate an ingest pipeline in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param docs: List of Documents to simulate in the ingest pipeline
        :type docs: list
        """
        pipeline = self.asdict()
        pipeline.pop("id")
        body = {"pipeline": pipeline, "docs": docs}
        ret = client.ingest.simulate(body, verbose=True)
        return ret
