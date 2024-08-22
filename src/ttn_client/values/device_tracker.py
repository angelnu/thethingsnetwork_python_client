"""Device Tracker value for The Thinks Network client."""

from .base import TTNBaseValue


class TTNDeviceTrackerValue(TTNBaseValue):
    """Sensor of type gps."""

    def __init__(self, uplink: dict, field_id: str, value) -> None:
        super().__init__(uplink, field_id, value)
        assert "latitude" in self.value
        assert "longitude" in self.value

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
    def altitude(self) -> float | None:
        """Return altitude value of the device."""
        return self.value.get("altitude", None)
