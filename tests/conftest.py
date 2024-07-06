"""Fixtures."""

import json
from unittest.mock import patch

import pytest

import ttn_client


@pytest.fixture
def dummy_client():
    """Test a basic connection to TTN."""
    client = ttn_client.TTNClient(
        hostname="eu1.cloud.thethings.network",
        application_id="home-assistant-casa",
        access_key="NNSXS.dummy",
    )
    assert client is not None
    return client


class MockContent:
    """Mock ahttp response content."""

    def __init__(self, data):
        self._content = data

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._content:
            content = self._content
            self._content = None
            return content
        else:
            raise StopAsyncIteration


class MockResponse:
    """Mock ahttp response."""

    def __init__(self, data, status, reason):
        self.content = MockContent(data)
        self.status = status
        self.reason = reason

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.fixture
def mock_aiohttp_client_session_get():
    """Patch ahttp to respond with given content and status."""

    def mock_get(data, status):
        resp = MockResponse(json.dumps(data), status, reason=None)
        return patch("ttn_client.client.aiohttp.ClientSession.get", return_value=resp)

    return mock_get
