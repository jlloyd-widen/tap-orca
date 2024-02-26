"""Tests standard tap features using the built-in SDK tests library."""

import json

from singer_sdk.testing import get_tap_test_class

from tap_orca.tap import TapOrca

SAMPLE_CONFIG = {
    "api_token": "test_api_token",
    "custom_streams": [
        {
            "name": "test_stream",
            "query": json.dumps({"test_query": "this"}),
        },
    ],
}


# Run standard built-in tap tests from the SDK:
TestTapOrca = get_tap_test_class(
    tap_class=TapOrca,
    config=SAMPLE_CONFIG,
)

