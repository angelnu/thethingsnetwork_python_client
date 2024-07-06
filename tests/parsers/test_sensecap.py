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
