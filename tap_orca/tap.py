"""Orca tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_orca.streams import DynamicOrcaStream
from tap_orca.client import OrcaStream


class TapOrca(Tap):
    """Orca tap class."""

    name = "tap-orca"

    custom_stream_config = th.ObjectType(
        th.Property(
            "name",
            th.StringType,
            required=False,
            description="The name of the custom stream."
        ),
        th.Property(
            "query",
            th.StringType,
            required=True,
            description="The query to run against the API."
        ),
        th.Property(
            "primary_keys",
            th.ArrayType(th.StringType),
            required=False,
            description="The primary keys for the custom stream."
        ),
        th.Property(
            "schema",
            th.ArrayType(th.StringType),
            required=False,
            description="A simple schema for the custom stream."
        ),
    )

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_token",
            th.StringType,
            required=True,
            secret=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "custom_streams",
            th.ArrayType(custom_stream_config),
            required=True,
            description="List of configs for custom streams.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[OrcaStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        streams = []
        for custom_stream in self.config.get("custom_streams"):
            streams.append(DynamicOrcaStream(
                tap=self,
                name=custom_stream.get("name"),
                query=custom_stream.get("query"),
                schema=self.discover_schema(custom_stream.get("query")),
                primary_keys=custom_stream.get("primary_keys"),
            ))
        return streams

    def discover_schema(self, query: str) -> dict:
        """Return the schema for a given query.

        Args:
            query: The query to run against the API.

        Returns:
            The schema for the stream.
        """
        schema = th.PropertiesList()
        stream = DynamicOrcaStream(
            tap=self,
            name="temp",
            query=query,
            schema=schema.to_dict()
        )

        # get an example from one query of the api
        self.logger.info("Discovering schema for custom stream")
        decorated_request = stream.request_decorator(stream._request)
        prepared_request = stream.prepare_request({}, next_page_token=0)
        resp = decorated_request(prepared_request, {})
        records = iter(stream.parse_response(resp))
        first_record = next(records)

        # accept any type for each key in the first record
        for key in first_record.keys():
            schema.append(
                th.Property(
                    key,
                    th.StringType(),
                    # th.CustomType(jsonschema_type_dict={
                    #     "anyOf": [
                    #         {"type": "null"},
                    #         {"type": "object"},
                    #         {"type": "array"},
                    #         {"type": "string"},
                    #         {"type": "number"},
                    #         # {"type": "boolean"},  # causes all values to be a boolean
                    #         {"type": "integer"},
                    #     ]
                    # })
                ),
            )
        self.logger.info("Schema discovery complete.")
        return schema.to_dict()


if __name__ == "__main__":
    TapOrca.cli()
