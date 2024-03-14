"""Test TTN client."""

import ttn_client


def test_connection():
    """Test a basic connection to TTN."""
    client = ttn_client.TTNClient(
        hostname="eu1.cloud.thethings.network",
        application_id="home-assistant-casa",
        access_key="NNSXS.dummy",
    )
    assert client is not None

    # TBD: add client.fetch_data() - need test env and test credentials as I cannot use my home one for a public pipeline
