"""Client for The Thinks Network."""

from collections.abc import Awaitable, Callable
from datetime import datetime
import json
import logging

import aiohttp
from aiohttp.hdrs import ACCEPT, AUTHORIZATION

from .const import DEFAULT_TIMEOUT, TTN_DATA_STORAGE_URL
from .values import TTNBaseValue
from .exceptions import TTNAuthError
from .parsers import ttn_parse

_LOGGER = logging.getLogger(__name__)


class TTNClient:  # pylint: disable=too-few-public-methods
    """Client to connect to the Things Network."""

    DATA_TYPE = dict[str, dict[str, TTNBaseValue]]

    def __init__(  # pylint: disable=too-many-arguments
        self,
        hostname: str,
        application_id: str,
        access_key: str,
        first_fetch_h: int = 24,
        push_callback: Callable[[DATA_TYPE], Awaitable[None]] | None = None,
    ) -> None:
        self.__hostname = hostname
        self.__application_id = application_id
        self.__access_key = access_key
        self.__first_fetch_h = first_fetch_h
        self.__push_callback = push_callback  # TBD: add support for MQTT to get faster updates # pylint: disable=W0238

        self.__last_measurement_datetime: datetime | None = None

    async def fetch_data(self) -> DATA_TYPE:
        """Fetch data stored by the TTN Storage since the last time we fetched/received data."""

        if not self.__last_measurement_datetime:
            fetch_last = f"{self.__first_fetch_h}h"
            _LOGGER.info("First fetch of tth data: %s", fetch_last)
        else:
            # Fetch new measurements since last time (with an extra minute margin)
            delta = datetime.now() - self.__last_measurement_datetime
            delta_s = delta.total_seconds()
            fetch_last = f"{delta_s}s"
            _LOGGER.info("Fetch of ttn data: %s", fetch_last)
        self.__last_measurement_datetime = datetime.now()

        # Discover entities
        # See API docs
        # at https://www.thethingsindustries.com/docs/reference/api/storage_integration/
        return await self.__storage_api_call(f"?last={fetch_last}&order=received_at")

    async def __storage_api_call(self, options) -> DATA_TYPE:
        url = TTN_DATA_STORAGE_URL.format(
            app_id=self.__application_id, hostname=self.__hostname, options=options
        )
        _LOGGER.debug("URL: %s", url)
        headers = {
            ACCEPT: "text/event-stream",
            AUTHORIZATION: f"Bearer {self.__access_key}",
        }

        session_timeout = aiohttp.ClientTimeout(DEFAULT_TIMEOUT)
        async with aiohttp.ClientSession(
            timeout=session_timeout
        ) as session, session.get(
            url, allow_redirects=False, timeout=DEFAULT_TIMEOUT, headers=headers
        ) as response:
            if response.status in range(400, 500):
                # LOGGER.error("Not authorized for Application ID: %s", self.__application_id)
                raise TTNAuthError

            if response.status not in range(200, 300):
                raise RuntimeError(
                    f"expected 200 got {response.status} - {response.reason}",
                )

            ttn_values: TTNClient.DATA_TYPE = {}
            async for application_up_raw in response.content:
                # Skip empty lines not containing a result
                if len(application_up_raw) < len("result"):
                    continue

                _LOGGER.debug("TTN entry: %s", application_up_raw)

                # Parse line with json dictionary
                application_up_json = json.loads(application_up_raw)

                if "result" not in application_up_json:
                    _LOGGER.error("TTN entry without result: %s", application_up_json)
                    continue

                application_up = application_up_json["result"]

                # Get device_id and uplink_message from measurement
                device_id = application_up["end_device_ids"]["device_id"]

                ttn_values[device_id] = ttn_parse(application_up)

        return ttn_values
