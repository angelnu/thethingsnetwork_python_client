"""Test TTN client."""

import pathlib
import json
import pytest

from ttn_client import TTNSensorValue
from ttn_client.parsers import ttn_parse


@pytest.fixture
def json_config(request):
    file = pathlib.Path(request.node.fspath.strpath)
    config = file.parent.joinpath("test_data", "cajenne.json")
    with config.open() as fp:
        return json.load(fp)


def test_valid(json_config):
    ttn_values = ttn_parse(json_config["data"])
    assert isinstance(ttn_values["analog_in_3"], TTNSensorValue)
    assert isinstance(ttn_values["analog_in_3"].value, float)
    assert ttn_values["analog_in_3"].value == 3.1
    assert isinstance(ttn_values["analog_in_42"], TTNSensorValue)
    assert isinstance(ttn_values["analog_in_43"], TTNSensorValue)
    assert isinstance(ttn_values["digital_in_1"], TTNSensorValue)
    assert isinstance(ttn_values["illuminance_44"], TTNSensorValue)
    assert isinstance(ttn_values["raw"], TTNSensorValue)
    assert isinstance(ttn_values["temperature_41"], TTNSensorValue)
