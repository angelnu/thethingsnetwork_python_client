"""The Things Network's client constants."""

from typing import Final

from aiohttp import ClientTimeout


DEFAULT_TIMEOUT: Final[ClientTimeout] = ClientTimeout(total=10 * 60)
TTN_DATA_STORAGE_URL = (
    "https://{hostname}/api/v3/as/applications/"
    "{app_id}/packages/storage/uplink_message{options}"
)
