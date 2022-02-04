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
    id: str
    last_modified: datetime
    pipeline: str
    pipeline_metadata: dict
    pipeline_settings: dict
    username: str
    description: Optional[str] = None

    def asdict(self):
        d = super().asdict()
        d["last_modified"] = time_format(d["last_modified"])
        return d

    @classmethod
    def get(cls, client, pipeline_id):
        """
        Get a logstash pipeline from Elasticsearch
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
        body = self.asdict()
        body.pop("id")
        return client.logstash.put_pipeline(id=self.id, body=body)

    def delete(self, client):
        try:
            return client.logstash.delete_pipeline(id=self.id)
        except Exception as e:
            raise e

    def update(self, client):
        return self.create(client)
