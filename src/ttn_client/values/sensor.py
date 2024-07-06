"""Sensor value for The Thinks Network client."""

from .base import TTNBaseValue


class TTNSensorValue(TTNBaseValue):
    """Sensor of type str, int or float."""

    @property
    def value(self) -> str | int | float:
        """the value itself."""
        return self._value
