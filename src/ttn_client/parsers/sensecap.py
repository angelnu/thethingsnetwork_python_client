"""Sensecap parser for for The Thinks Network client."""

import logging
from ..values import TTNBaseValue, TTNSensorValue

# pylint: disable=duplicate-code
_LOGGER = logging.getLogger(__name__)


def sensecap_parser(uplink_data: dict) -> dict[str, TTNBaseValue]:
    """Sensecap parser for for The Thinks Network client."""

    ttn_values: dict[str, TTNBaseValue] = {}

    # Get device_id and uplink_message from measurement
    device_id = uplink_data["end_device_ids"]["device_id"]
    uplink_message = uplink_data["uplink_message"]

    # Skip not decoded measurements
    if "decoded_payload" not in uplink_message:
        _LOGGER.warning("No decoded_payload for device %s", device_id)
    else:
        decoded_payload = uplink_message["decoded_payload"]
        # Check im msg is valid
        if not decoded_payload["valid"]:
            _LOGGER.warning(
                "Ignoring message marked as invalid for device %s: %s",
                device_id,
                decoded_payload,
            )
        else:
            # Create values for fixed msgs
            for field in ["err", "payload"]:
                ttn_values[field] = TTNSensorValue(
                    uplink_data, field, decoded_payload[field]
                )
            if "messages" not in decoded_payload:
                _LOGGER.warning("No messages for device %s", device_id)
            else:
                # Parse messages
                messages = decoded_payload["messages"]
                for value_item in messages:
                    __sensecap_parse_msg(
                        ttn_values,
                        device_id,
                        uplink_data,
                        value_item,
                    )
    return ttn_values


def __sensecap_parse_msg(
    ttn_values: dict[str, TTNBaseValue],
    device_id: str,
    uplink_data: dict,
    value_item,
) -> None:
    """Parses a Sensecap field"""

    if isinstance(value_item, dict):
        battery = value_item.get("Battery(%)")
        measurement_id = value_item.get("measurementId")
        measurement_value = value_item.get("measurementValue")
        measurement_type = value_item.get("type")

        if battery:
            ttn_values["battery"] = TTNSensorValue(uplink_data, "battery", battery)
            return
        if measurement_id and measurement_value and measurement_type:
            field_id = f"{measurement_type.replace(' ','_')}_{measurement_id}"
            ttn_values[field_id] = TTNSensorValue(
                uplink_data, field_id, measurement_value
            )

    _LOGGER.warning(
        "Message for device %s ignored (type %s): %s",
        device_id,
        type(value_item),
        value_item,
    )
