"""Parsers for for The Thinks Network client."""

from ..values import TTNBaseValue
from .default import default_parser


def ttn_parse(uplink_data: dict) -> dict[str, TTNBaseValue]:
    """Return a parser for the device."""

    parser = default_parser

    return parser(uplink_data)
