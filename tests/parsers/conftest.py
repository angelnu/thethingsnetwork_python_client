"""Fixtures."""

import json
import pathlib

import pytest


def json_config(request, test_file):
    file = pathlib.Path(request.node.fspath.strpath)
    config = file.parent.joinpath("test_data", test_file)
    with config.open() as fp:
        return json.load(fp)


@pytest.fixture
def default_valid(request):
    return json_config(request, "default_valid.json")


@pytest.fixture
def default_no_decoded_payload(request):
    return json_config(request, "default_no_decoded_payload.json")


@pytest.fixture
def sensecap_valid(request):
    return json_config(request, "sensecap_valid.json")
