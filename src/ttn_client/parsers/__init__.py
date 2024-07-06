"""Parsers for for The Thinks Network client."""

from ..values import TTNBaseValue
from .default import default_parser
from .sensecap import sensecap_parser


def ttn_parse(uplink_data: dict) -> dict[str, TTNBaseValue]:
    """Return a parser for the device."""

    version_ids = uplink_data.get("uplink_message", {}).get("version_ids", {})
    version_ids = uplink_data["uplink_message"].get("version_ids", {})
    brand_id = version_ids.get("brand_id", {})
    # model_id = version_ids.get("model_id", {})
    # hardware_version = version_ids.get("hardware_version", {})
    # firmware_version = version_ids.get("firmware_version", {})

    if brand_id == "sensecap":
        parser = sensecap_parser
    else:
        parser = default_parser

    return parser(uplink_data)
