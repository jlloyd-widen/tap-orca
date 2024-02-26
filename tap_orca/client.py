"""GraphQL client handling, including OrcaStream base class."""

from __future__ import annotations

from singer_sdk.pagination import BaseAPIPaginator, BaseOffsetPaginator
from singer_sdk.streams import GraphQLStream
from singer_sdk.streams.rest import _TToken


class OrcaStream(GraphQLStream):
    """Orca stream class."""

    records_jsonpath: str = "$.data[*]"
    page_size = 1000  # chunk size, can be between 1 and 1000
    stream_config = None

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return "https://app.us.orcasecurity.io/api/sonar/query"

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "Authorization": f"Token {self.config.get('api_token')}",
        }

    def prepare_request_payload(
            self,
            context: dict | None,
            next_page_token: _TToken | None,
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Developers may override this method if the API requires a custom payload along
        with the request. (This is generally not required for APIs which use the
        HTTP 'GET' method.)

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.
        """
        return {
            "query": self.query,
            "limit": self.page_size,
            "enable_pagination": "true",
            "get_results_and_count": "true",
            "ui": "false",
            "start_at_index": next_page_token
        }

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Get a fresh paginator for this API endpoint.

        Returns:
            A paginator instance.
        """
        return BaseOffsetPaginator(0, self.page_size)

    def post_process(self, row: dict, context: dict) -> dict:
        """Post-process the record before writing it."""
        return {k: str(v) for k, v in row.items()}
