"""Stream type classes for tap-orca."""

from __future__ import annotations

import json
import sys
import typing as t

from tap_orca.client import OrcaStream

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources


class DynamicOrcaStream(OrcaStream):
    """Define custom stream."""

    def __init__(
        self,
        tap,
        name: str,
        query: dict | str,
        schema: dict,
        primary_keys: t.ClassVar[list[str]] = ["id"],
        replication_key=None,
        **kwargs
    ):
        super().__init__(tap, name, schema, **kwargs)
        self.name = name
        self.custom_query = query
        self.primary_keys = primary_keys
        self.replication_key = replication_key

    @property
    def query(self) -> dict:
        """Return the GraphQL query to run against the API."""
        if isinstance(self.custom_query, str):
            return json.loads(self.custom_query)
        return self.custom_query
