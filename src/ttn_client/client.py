"""Client for The Thinks Network."""

from collections.abc import Awaitable, Callable
from datetime import datetime
import json
import logging

import aiohttp
from aiohttp.hdrs import ACCEPT, AUTHORIZATION

from .const import DEFAULT_TIMEOUT, TTN_DATA_STORAGE_URL

_LOGGER = logging.getLogger(__name__)


# define Python user-defined exceptions
class TTNAuthError(Exception):
    "Raised when we get 4xx."


class TTNBaseValue:
    """Represents a TTN sensor value and includes metadata from the uplink message."""

    def __init__(self, uplink: dict, field_id: str, value) -> None:
        self.__uplink = uplink
        self.__field_id = field_id
        self._value = value

    @property
    def uplink(self) -> dict:
        """raw uplink message."""
        return self.__uplink

    @property
    def field_id(self) -> str:
        """field_id representing this value-"""
        return self.__field_id

    @property
    def value(self):
        """the value itself."""
        return str(self._value)

    @property
    def received_at(self) -> datetime:
        """the datetime the value was received."""
        # Example: 2024-03-11T08:49:11.153738893Z
        return datetime.fromisoformat(self.uplink["received_at"])

    @property
    def device_id(self) -> str:
        """device_id for this value."""
        return self.uplink["end_device_ids"]["device_id"]

    def __repr__(self) -> str:
        return f"TTN_Value({self.value})"


class TTNSensorValue(TTNBaseValue):
    """Sensor of type str, int or float."""

    @property
    def value(self) -> str | int | float:
        """the value itself."""
        return self._value


class TTNBinarySensorValue(TTNBaseValue):
    """Sensor of type bool."""

    @property
    def value(self) -> bool:
        """the value itself."""
        return self._value


class TTNDeviceTrackerValue(TTNBaseValue):
    """Sensor of type gps."""

    @property
    def value(self) -> dict:
        """the value itself."""
        return self._value

    @property
    def latitude(self) -> float:
        """Return latitude value of the device."""
        return self.value["latitude"]

    @property
    def longitude(self) -> float:
        """Return longitude value of the device."""
        return self.value["longitude"]

    @property
    def altitude(self) -> float:
        """Return altitude value of the device."""
        return self.value["altitude"]


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
                uplink_message = application_up["uplink_message"]

                # Skip not decoded measurements
                if "decoded_payload" not in uplink_message:
                    continue

                ttn_values.setdefault(device_id, {})
                for field_id, value_item in uplink_message["decoded_payload"].items():
                    TTNClient.__add_value(
                        ttn_values,
                        device_id,
                        field_id,
                        application_up,
                        value_item,
                    )

        return ttn_values

    @staticmethod
    def __add_value(
        ttn_values: DATA_TYPE,
        device_id: str,
        field_id: str,
        application_up: dict,
        new_value,
    ) -> None:
        new_ttn_value: TTNBaseValue | None
        if isinstance(new_value, dict):
            if "gps" in field_id:
                # GPS
                new_ttn_value = TTNDeviceTrackerValue(
                    application_up, field_id, new_value
                )
            else:
                # Other - such as acceleration -> split in multiple ttn_values
                for key, value_item in new_value.items():
                    TTNClient.__add_value(
                        ttn_values,
                        device_id,
                        f"{field_id}_{key}",
                        application_up,
                        value_item,
                    )
                return
        elif isinstance(new_value, bool):
            # BinarySensor
            new_ttn_value = TTNBinarySensorValue(application_up, field_id, new_value)
        elif isinstance(new_value, list):
            # TTN_SensorValue with list as string
            new_ttn_value = TTNSensorValue(application_up, field_id, str(new_value))
        elif isinstance(new_value, (str, int, float)):
            new_ttn_value = TTNSensorValue(application_up, field_id, new_value)
        else:
            raise TypeError(f"Unexpected type {type(new_value)} for value: {new_value}")

        ttn_values[device_id][field_id] = new_ttn_value
