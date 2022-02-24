#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch import NotFoundError
import dacite
from dataclasses import dataclass, field
from typing import Optional
from nemesis.resources import enforce_types, BaseResource
from nemesis.schemas.elasticsearch.logstash_pipeline import LogstashPipelineSchema


def time_format(dt):
    """
    timeformat must match Elasticsearch `strict_date_time` format:
    https://www.elastic.co/guide/en/elasticsearch/reference/7.16/mapping-date-format.html
    """
    s = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
    return f"{s[:-3]}Z"


@enforce_types
@dataclass(repr=False, frozen=True)
class LogstashPipeline(BaseResource):
    """
    Manage a `Logstash Pipeline <https://www.elastic.co/guide/en/elasticsearch/reference/current/logstash-api-put-pipeline.html>`__

    :param id: id of the Logstash Pipeline.
    :type id: str

    :param last_modified: Timestamp for the logstash pipeline to track when it was last modified.
    :type last_modified: datetime, optional

    :param pipeline: String representation of the logstash pipeline.
    :type pipeline: str

    :param pipeline_metadata: Optional metadata for the logstash pipeline
    :type pipeline_metadata: dict, optional

    :param pipeline_settings: Optional settings for the logstash pipeline
    :type pipeline_settings: dict, optional

    :param username: username of the person or account who edited the logstash pipeline
    :type username: str, optional

    :param description: Description of the logstash pipeline
    :type description: str, optional

    """

    id: str
    last_modified: datetime
    pipeline: str
    pipeline_metadata: dict
    pipeline_settings: dict
    username: str
    description: Optional[str] = None

    def asdict(self):
        """
        Return Logstash Pipeline as a dictionary
        """
        d = super().asdict()
        d["last_modified"] = time_format(d["last_modified"])
        return d

    @classmethod
    def get(cls, client, pipeline_id):
        """
        Get a logstash pipeline from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        :param pipeline_id: Ingest pipeline id
        :type pipeline_id: str
        """
        try:
            pipeline = client.logstash.get_pipeline(id=pipeline_id)
        except NotFoundError:
            return None
        schema = LogstashPipelineSchema()
        result = schema.load(pipeline)
        pipeline = dacite.from_dict(data_class=cls, data=result)
        return pipeline

    def create(self, client):
        """
        Create a logstash pipeline in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        body = self.asdict()
        body.pop("id")
        return client.logstash.put_pipeline(id=self.id, body=body)

    def delete(self, client):
        """
        Delete a logstash pipeline from Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`
        """
        try:
            return client.logstash.delete_pipeline(id=self.id)
        except Exception as e:
            raise e

    def update(self, client):
        """
        Update a logstash pipeline in Elasticsearch

        :param client: Elasticsearch Client
        :type client: :py:mod:`Elasticsearch`

        """
        return self.create(client)
