"""Binary Sensor value for The Thinks Network client."""

from .base import TTNBaseValue


class TTNBinarySensorValue(TTNBaseValue):
    """Sensor of type bool."""

    @property
    def value(self) -> bool:
        """the value itself."""
        return self._value
