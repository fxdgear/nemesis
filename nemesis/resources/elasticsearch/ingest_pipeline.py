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
        body = self.asdict()
        body.pop("id")
        return client.ingest.put_pipeline(id=self.id, body=body)

    def delete(self, client):
        try:
            return client.ingest.delete_pipeline(id=self.id)
        except Exception as e:
            raise e

    def update(self, client):
        return self.create(client)

    def simulate(self, client, docs):
        pipeline = self.asdict()
        pipeline.pop("id")
        body = {"pipeline": pipeline, "docs": docs}
        ret = client.ingest.simulate(body, verbose=True)
        return ret
