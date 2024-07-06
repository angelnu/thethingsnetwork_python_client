"""Test default parser."""

import datetime
import pytest

from ttn_client import (
    TTNSensorValue,
    TTNBaseValue,
    TTNBinarySensorValue,
    TTNDeviceTrackerValue,
)
from ttn_client.parsers import ttn_parse


def test_default_valid(default_valid):
    """Test valid default msg."""
    uplink_data = default_valid["data"]
    ttn_values = ttn_parse(uplink_data)

    # Test TTNBaseValue
    assert isinstance(ttn_values["analog_in_3"], TTNBaseValue)
    sensor_value = ttn_values["analog_in_3"]
    base_value = super(TTNSensorValue, sensor_value)
    assert str(sensor_value) == "TTN_Value(3.1)"
    assert base_value.value == "3.1"
    assert base_value.uplink == uplink_data
    assert base_value.field_id == "analog_in_3"
    assert base_value.received_at == datetime.datetime(
        2024, 7, 6, 9, 19, 21, 381960, tzinfo=datetime.timezone.utc
    )
    assert base_value.device_id == "distance-03"

    # Test TTNSensorValue - float
    sensor_value = ttn_values["analog_in_3"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, float)
    assert sensor_value.value == 3.1

    # Test TTNSensorValue - int
    sensor_value = ttn_values["digital_in_1"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, int)
    assert sensor_value.value == 8

    # Test TTNSensorValue - str
    sensor_value = ttn_values["raw"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, str)
    assert sensor_value.value == (
        "[1, 0, 8, 1, 0, 8, 3, 2, 1, 54, 41, 103, 0, 246,"
        " 42, 2, 2, 88, 43, 2, 15, 96, 44, 101, 7, 216]"
    )

    # Test TTNBinarySensorValue
    sensor_value = ttn_values["boolean_1"]
    assert isinstance(sensor_value, TTNBinarySensorValue)
    assert isinstance(sensor_value.value, bool)
    assert sensor_value.value

    # Test TTNDeviceTrackerValue
    sensor_value = ttn_values["gps_34"]
    assert isinstance(sensor_value, TTNDeviceTrackerValue)
    assert isinstance(sensor_value.value, dict)
    assert sensor_value.value == {
        "altitude": 310,
        "latitude": 48.76826575,
        "longitude": 9.1596689,
    }
    assert sensor_value.altitude == 310
    assert sensor_value.latitude == 48.76826575
    assert sensor_value.longitude == 9.1596689

    # Test object
    sensor_value = ttn_values["accelerometer_77_x"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, int)
    assert sensor_value.value == 1
    sensor_value = ttn_values["accelerometer_77_y"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, float)
    assert sensor_value.value == 0.5
    sensor_value = ttn_values["accelerometer_77_z"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, float)
    assert sensor_value.value == 9.8

    # Test all other fields were parsed
    assert isinstance(ttn_values["analog_in_42"], TTNSensorValue)
    assert isinstance(ttn_values["analog_in_43"], TTNSensorValue)
    assert isinstance(ttn_values["digital_in_1"], TTNSensorValue)
    assert isinstance(ttn_values["illuminance_44"], TTNSensorValue)
    assert isinstance(ttn_values["raw"], TTNSensorValue)
    assert isinstance(ttn_values["temperature_41"], TTNSensorValue)


def test_default_no_decoded_payload(default_no_decoded_payload):
    """Test msg without decoded payload."""
    ttn_values = ttn_parse(default_no_decoded_payload["data"])
    assert not ttn_values


def test_default_none_value(default_valid):
    """Test msg with None field value."""
    ttn_values = ttn_parse(default_valid["data"])

    uplink_with_none_value = default_valid["data"]
    uplink_with_none_value["uplink_message"]["decoded_payload"]["digital_in_1"] = None
    ttn_values_with_none = ttn_parse(uplink_with_none_value)
    assert len(ttn_values_with_none) == len(ttn_values) - 1


def test_default_unexpected_value(default_valid):
    """Test msg with unexpected field vault."""

    uplink_with_unexpected_value = default_valid["data"]
    uplink_with_unexpected_value["uplink_message"]["decoded_payload"][
        "digital_in_1"
    ] = object
    with pytest.raises(TypeError) as e_info:
        ttn_parse(uplink_with_unexpected_value)

    assert (
        str(e_info.value)
        == "Unexpected type <class 'type'> for value: <class 'object'>"
    )
