"""Fixtures."""

import json
import pathlib

import pytest


def json_config(request, test_file):
    file = pathlib.Path(request.node.fspath.strpath)
    config = file.parent.joinpath("test_data", test_file)
    with config.open(encoding="utf-8") as fp:
        return json.load(fp)


@pytest.fixture
def default_valid(request):
    return json_config(request, "default_valid.json")


@pytest.fixture
def default_no_decoded_payload(request):
    return json_config(request, "default_no_decoded_payload.json")


@pytest.fixture
def default_sensor_attr(request):
    return json_config(request, "default_sensor_attr.json")


@pytest.fixture
def sensecap_valid(request):
    return json_config(request, "sensecap_valid.json")


@pytest.fixture
def sensecap_t1000_nested(request):
    return json_config(request, "sensecap_t1000_nested.json")
