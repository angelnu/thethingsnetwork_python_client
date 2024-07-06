"""Parsers for for The Thinks Network client."""

from ..values import TTNBaseValue
from .cayenne import cayenne_parser


def ttn_parse(uplink_data: dict) -> dict[str, TTNBaseValue]:
    """Return a parser for the device."""

    parser = cayenne_parser

    return parser(uplink_data)
