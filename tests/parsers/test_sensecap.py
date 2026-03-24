"""Test sensecap parser."""

import datetime

from ttn_client import TTNSensorValue, TTNBaseValue
from ttn_client.parsers import ttn_parse


def test_sensecap_valid(sensecap_valid):
    """Test valid sensecap msg."""
    uplink_data = sensecap_valid["data"]
    ttn_values = ttn_parse(uplink_data)

    # Test TTNBaseValue
    fieldId = "Air_Temperature_4097"
    sensor_value = ttn_values[fieldId]
    assert isinstance(sensor_value, TTNBaseValue)
    base_value = super(TTNSensorValue, sensor_value)
    assert str(sensor_value) == "TTN_Value(13.3)"
    assert base_value.value == "13.3"
    assert base_value.uplink == uplink_data
    assert base_value.field_id == fieldId
    assert base_value.received_at == datetime.datetime(
        2024, 7, 5, 16, 16, 30, 899243, tzinfo=datetime.timezone.utc
    )
    assert base_value.device_id == "eui-2cf7f1c044300279"

    # Test TTNSensorValue - float
    fieldId = "Air_Temperature_4097"
    sensor_value = ttn_values[fieldId]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, float)
    assert sensor_value.value == 13.3

    # Test TTNSensorValue - int
    fieldId = "Air_Humidity_4098"
    sensor_value = ttn_values[fieldId]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, int)
    assert sensor_value.value == 77

    # Test TTNSensorValue - Battery
    fieldId = "battery"
    sensor_value = ttn_values[fieldId]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, int)
    assert sensor_value.value == 100

    # Test TTNSensorValue - err
    fieldId = "err"
    sensor_value = ttn_values[fieldId]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, int)
    assert sensor_value.value == 0

    # Test TTNSensorValue - payload
    fieldId = "payload"
    sensor_value = ttn_values[fieldId]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, str)
    assert sensor_value.value == "0100854D00000F4700001502007F0000000026EE0364"


def test_sensecap_no_decoded_payload(sensecap_valid):
    """Test sensecap without decoder"""
    uplink_data = sensecap_valid["data"]
    del uplink_data["uplink_message"]["decoded_payload"]
    ttn_values = ttn_parse(uplink_data)
    assert len(ttn_values) == 0


def test_sensecap_invalid_payload(sensecap_valid):
    """Test invalid sensecap msg."""
    uplink_data = sensecap_valid["data"]
    uplink_data["uplink_message"]["decoded_payload"]["valid"] = False
    ttn_values = ttn_parse(uplink_data)
    assert len(ttn_values) == 0


def test_sensecap_no_messages(sensecap_valid):
    """Test sensecap without decoder"""
    uplink_data = sensecap_valid["data"]
    del uplink_data["uplink_message"]["decoded_payload"]["messages"]
    ttn_values = ttn_parse(uplink_data)
    assert len(ttn_values) == 2


def test_sensecap_t1000_nested_valid(sensecap_t1000_nested):
    """Test valid T1000 msg with nested list structure."""
    uplink_data = sensecap_t1000_nested["data"]
    ttn_values = ttn_parse(uplink_data)

    # Test that basic fields are present
    assert "err" in ttn_values
    assert "payload" in ttn_values

    # Test err value
    sensor_value = ttn_values["err"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert sensor_value.value == 0

    # Test payload value
    sensor_value = ttn_values["payload"]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, str)

    # Test Wi-Fi Scan measurement (measurementId 5001)
    field_id = "Wi-Fi_Scan_5001"
    assert field_id in ttn_values
    sensor_value = ttn_values[field_id]
    assert isinstance(sensor_value, TTNSensorValue)
    assert isinstance(sensor_value.value, list)
    assert len(sensor_value.value) == 4
    # Verify Wi-Fi scan data structure
    assert sensor_value.value[0]["mac"] == "AA:BB:CC:DD:EE:01"
    assert sensor_value.value[0]["rssi"] == "-68"

    # Test Battery measurement (measurementId 3000)
    field_id = "Battery_3000"
    assert field_id in ttn_values
    sensor_value = ttn_values[field_id]
    assert isinstance(sensor_value, TTNSensorValue)
    assert sensor_value.value == 88

    # Test device metadata
    assert sensor_value.device_id == "test-t1000-device"


def test_sensecap_t1000_nested_backward_compat(sensecap_valid):
    """Test that flat array format (S2120) still works after fix."""
    uplink_data = sensecap_valid["data"]
    ttn_values = ttn_parse(uplink_data)

    # Verify that original flat format tests still pass
    assert "Air_Temperature_4097" in ttn_values
    assert "Air_Humidity_4098" in ttn_values
    assert "battery" in ttn_values

    # Verify values are correct
    assert ttn_values["Air_Temperature_4097"].value == 13.3
    assert ttn_values["Air_Humidity_4098"].value == 77
    assert ttn_values["battery"].value == 100


def test_sensecap_t1000_mixed_format(sensecap_t1000_nested):
    """Test mixed format with both nested and flat items in messages array."""
    uplink_data = sensecap_t1000_nested["data"]

    # Modify to have mixed format: first item is nested, second is flat
    decoded_payload = uplink_data["uplink_message"]["decoded_payload"]
    flat_item = {
        "measurementId": "4097",
        "measurementValue": 25.5,
        "type": "Air Temperature"
    }
    decoded_payload["messages"].append(flat_item)

    ttn_values = ttn_parse(uplink_data)

    # Verify nested items are parsed
    assert "Wi-Fi_Scan_5001" in ttn_values
    assert "Battery_3000" in ttn_values

    # Verify flat item is also parsed
    assert "Air_Temperature_4097" in ttn_values
    assert ttn_values["Air_Temperature_4097"].value == 25.5
