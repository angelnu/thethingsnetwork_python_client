# The Things Network_python_client

[![codecov](https://codecov.io/gh/angelnu/thethingsnetwork_python_client/graph/badge.svg?token=yUTImnfbUL)](https://codecov.io/gh/angelnu/thethingsnetwork_python_client)
[![PyPI version](https://badge.fury.io/py/ttn-client.svg)](https://badge.fury.io/py/ttn-client)

A python client to fetch/receive and parse uplink messages from The Things Network

It is used primarily for the [home-assistant integration](https://www.home-assistant.io/integrations/thethingsnetwork/) but it should also work independently - check the [testcases](tests).

## Assumptions

For this library to work, the [TheThingNetwork storage plugin](https://www.thethingsindustries.com/docs/integrations/storage/) is required. You might also check the [home assistant prerequisites](https://www.home-assistant.io/integrations/thethingsnetwork/#prerequisites) as they also apply when this library is used standalone.

A [payload decoded](https://www.thethingsindustries.com/docs/integrations/payload-formatters/) needs to be present so that you have a `decoded_payload` in the uplink message. By default, this library expects the `decoded_payload` to have a key-value format such as:

```json5
"decoded_payload": {
          "accelerometer_77": {
            "x": 1,  # Sensor will be called accelerometer_77_x
            "y": 0.5,  # Sensor will be called accelerometer_77_y
            "z": 9.8   # Sensor will be called accelerometer_77_z
          },
          "voltage": 3.1,  # Sensor will be called voltage and be of type float
          "boolean_1": true,  # Binary Sensor will be called boolean_1
          "digital_in_1": 8,  # Sensor will be called voltage and be of type int
          "gps_34": {  # Device Tracker will be called gps_34
            "latitude": 48.76826575,
            "longitude": 9.1596689,
            "altitude": 310
          }
        }
```

If you have a device using a different format, please open an [Issue](issues) and post a copy of **full** message for your device.

## Supported devices

- [Default](tests/parsers/test_data/default_valid.json)
- [Sensecap](tests/parsers/test_data/sensecap_valid.json)

## Thanks

This package structure and pipeline is derived from the [zwave-js-server-python](https://github.com/home-assistant-libs/zwave-js-server-python) package.
