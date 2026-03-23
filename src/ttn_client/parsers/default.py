"""Cayenne parser for for The Thinks Network client."""

import logging
from ..values import (
    TTNBaseValue,
    TTNBinarySensorValue,
    TTNDeviceTrackerValue,
    TTNSensorAttribute,
    TTNSensorValue,
)

_LOGGER = logging.getLogger(__name__)

_SENSOR_ATTR_KEY = "_sensor_attr"


def default_parser(uplink_data: dict) -> dict[str, TTNBaseValue]:
    """Cayenne parser for for The Thinks Network client."""

    ttn_values: dict[str, TTNBaseValue] = {}

    # Get device_id and uplink_message from measurement
    device_id = uplink_data["end_device_ids"]["device_id"]
    uplink_message = uplink_data["uplink_message"]

    # Skip not decoded measurements
    if "decoded_payload" not in uplink_message:
        _LOGGER.warning("No decoded_payload for device %s", device_id)
    else:
        for field_id, value_item in uplink_message["decoded_payload"].items():
            __default_parse_field(
                ttn_values,
                field_id,
                uplink_data,
                value_item,
            )
    return ttn_values


def __default_parse_field(
    ttn_values: dict[str, TTNBaseValue],
    field_id: str,
    application_up: dict,
    new_value,
) -> None:
    """Parses a cayenne field"""
    new_ttn_value: TTNBaseValue | None
    if isinstance(new_value, dict):
        if "latitude" in new_value and "longitude" in new_value:
            # GPS
            new_ttn_value = TTNDeviceTrackerValue(application_up, field_id, new_value)
        elif field_id == _SENSOR_ATTR_KEY:
            # _sensor_attr: { BatV: { unit: "V", device_class: "voltage" } }
            for sensor_field, attr_dict in new_value.items():
                if not isinstance(attr_dict, dict):
                    continue
                for attr_key, attr_value in attr_dict.items():
                    flat_key = f"{_SENSOR_ATTR_KEY}_{sensor_field}_{attr_key}"
                    ttn_values[flat_key] = TTNSensorAttribute(
                        application_up, flat_key, str(attr_value)
                    )
            return
        else:
            # Other - such as acceleration -> split in multiple ttn_values
            for key, value_item in new_value.items():
                __default_parse_field(
                    ttn_values,
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
    elif new_value is None:
        # Skip null values
        _LOGGER.warning(
            "Ignoring entry %s with value=None - check your application decoder",
            field_id,
        )
        return
    else:
        raise TypeError(f"Unexpected type {type(new_value)} for value: {new_value}")

    ttn_values[field_id] = new_ttn_value
