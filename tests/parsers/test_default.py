"""Test default parser."""

import datetime
import pytest

from ttn_client import (
    TTNBaseValue,
    TTNBinarySensorValue,
    TTNDeviceTrackerValue,
    TTNSensorAttribute,
    TTNSensorValue,
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


def test_sensor_attr_parsed_as_attribute(default_sensor_attr):
    """Test _sensor_attr fields are parsed as TTNSensorAttribute."""
    ttn_values = ttn_parse(default_sensor_attr["data"])

    # BatV attributes
    assert isinstance(ttn_values["_sensor_attr_BatV_unit"], TTNSensorAttribute)
    assert ttn_values["_sensor_attr_BatV_unit"].value == "V"
    assert ttn_values["_sensor_attr_BatV_device_class"].value == "voltage"
    assert ttn_values["_sensor_attr_BatV_state_class"].value == "measurement"
    assert ttn_values["_sensor_attr_BatV_entity_category"].value == "diagnostic"

    # TempC_SHT attributes
    assert isinstance(ttn_values["_sensor_attr_TempC_SHT_unit"], TTNSensorAttribute)
    assert ttn_values["_sensor_attr_TempC_SHT_unit"].value == "°C"
    assert ttn_values["_sensor_attr_TempC_SHT_device_class"].value == "temperature"

    # repr
    assert repr(ttn_values["_sensor_attr_BatV_unit"]) == "TTN_Attr(V)"


def test_sensor_attr_flat_keys(default_sensor_attr):
    """Test all expected flat keys are present."""
    ttn_values = ttn_parse(default_sensor_attr["data"])

    expected_attr_keys = {
        "_sensor_attr_BatV_unit",
        "_sensor_attr_BatV_device_class",
        "_sensor_attr_BatV_state_class",
        "_sensor_attr_BatV_entity_category",
        "_sensor_attr_TempC_SHT_unit",
        "_sensor_attr_TempC_SHT_device_class",
    }
    actual_attr_keys = {
        k for k, v in ttn_values.items() if isinstance(v, TTNSensorAttribute)
    }
    assert actual_attr_keys == expected_attr_keys


def test_sensor_attr_non_dict_skipped(default_sensor_attr):
    """Test non-dict entries in _sensor_attr are skipped."""
    ttn_values = ttn_parse(default_sensor_attr["data"])

    # "invalid_entry": "not_a_dict" should be skipped
    invalid_keys = [k for k in ttn_values if "invalid_entry" in k]
    assert invalid_keys == []


def test_sensor_attr_normal_values_unchanged(default_sensor_attr):
    """Test normal sensor values are not affected by _sensor_attr."""
    ttn_values = ttn_parse(default_sensor_attr["data"])

    # Normal sensor values remain TTNSensorValue
    assert isinstance(ttn_values["BatV"], TTNSensorValue)
    assert ttn_values["BatV"].value == 3.016
    assert isinstance(ttn_values["TempC_SHT"], TTNSensorValue)
    assert ttn_values["TempC_SHT"].value == 24.6

    # Boolean still works
    assert isinstance(ttn_values["boolean_1"], TTNBinarySensorValue)


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
