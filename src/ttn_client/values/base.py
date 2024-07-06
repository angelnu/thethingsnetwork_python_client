"""Base value for The Thinks Network client."""

from datetime import datetime


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
