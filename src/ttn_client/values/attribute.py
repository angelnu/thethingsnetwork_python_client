"""Sensor attribute value for The Things Network client."""

from .base import TTNBaseValue


class TTNSensorAttribute(TTNBaseValue):
    """Holds a named attribute for a sensor field.

    TTN payload decoders can annotate sensor fields with arbitrary
    key-value pairs by returning a _sensor_attr object in the
    decoded payload.

    The attribute key names are defined by the decoder author and
    are not interpreted by ttn_client. Consumers (e.g. a Home
    Assistant integration) define the mapping from attribute names
    to their platform-specific concepts.
    """

    @property
    def value(self) -> str:
        """Return the attribute value."""
        return self._value

    def __repr__(self) -> str:
        return f"TTN_Attr({self._value})"
