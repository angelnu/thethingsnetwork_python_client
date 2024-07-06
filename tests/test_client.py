"""Test TTN client."""

import pytest

import ttn_client

pytest_plugins = "pytest_asyncio"


@pytest.mark.asyncio
async def test_mocked_connection(dummy_client, mock_aiohttp_client_session_get):
    """Test client with mocked data."""
    with mock_aiohttp_client_session_get(
        {"result": {"end_device_ids": {"device_id": "dummy"}, "uplink_message": {}}},
        200,
    ):
        await dummy_client.fetch_data()

    with mock_aiohttp_client_session_get({}, 200):
        await dummy_client.fetch_data()


@pytest.mark.asyncio
async def test_connection_auth_error(dummy_client):
    """Test that dummy credentials fail."""

    with pytest.raises(ttn_client.TTNAuthError):
        await dummy_client.fetch_data()


@pytest.mark.asyncio
async def test_invalid_get_status(dummy_client, mock_aiohttp_client_session_get):
    """Test client with mocked data."""
    with mock_aiohttp_client_session_get({}, 500):
        with pytest.raises(RuntimeError):
            await dummy_client.fetch_data()


@pytest.mark.asyncio
async def test_missing_result(dummy_client, mock_aiohttp_client_session_get):
    """Test client with mocked data."""

    with mock_aiohttp_client_session_get({"missing_result": {}}, 200):
        await dummy_client.fetch_data()
