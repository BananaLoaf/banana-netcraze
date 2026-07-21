# banana-netcraze

[![Python CI](https://github.com/BananaLoaf/banana-netcraze/actions/workflows/python-ci.yml/badge.svg?branch=master)](https://github.com/BananaLoaf/banana-netcraze/actions/workflows/python-ci.yml?query=branch%3Amaster)
[![PyPI](https://img.shields.io/pypi/v/banana-netcraze)](https://pypi.org/project/banana-netcraze/)
[![License](https://img.shields.io/pypi/l/banana-netcraze)](https://github.com/BananaLoaf/banana-netcraze/blob/master/LICENSE)

UNOFFICIAL Python library for Keenetic/Netcraze routers.

`banana-netcraze` is a small synchronous client for the router HTTP API. It
handles the router challenge-response authentication flow, keeps an `httpx`
session, and parses known responses into Pydantic models.

## Installation

### CLI Installation

For a standalone CLI installation with `pipx`:

```bash
pipx install "banana-netcraze[cli]"
banana-netcraze --help
```

To install the CLI persistently with `uv`, use `uv tool install`:

```bash
uv tool install "banana-netcraze[cli]"
banana-netcraze --help
```

To run the CLI without installing it permanently, use `uvx`:

```bash
uvx --from "banana-netcraze[cli]" banana-netcraze --help
uvx --from "banana-netcraze[cli]" banana-netcraze startup-config --password password --stdout
```

CLI options can also be provided through environment variables:

| Environment variable | CLI option | Description |
| --- | --- | --- |
| `NETCRAZE_URL` | `--url` | Router base URL. |
| `NETCRAZE_USERNAME` | `--username` | Router account username. |
| `NETCRAZE_PASSWORD` | `--password` | Router account password. |

For example:

```bash
export NETCRAZE_URL=http://192.168.1.1
export NETCRAZE_USERNAME=admin
export NETCRAZE_PASSWORD=password
banana-netcraze startup-config --stdout > startup-config.txt
```

### Library Installation

To use `banana-netcraze` as a Python library:

```bash
pip install banana-netcraze
```

Or with `uv`:

```bash
uv add banana-netcraze
```

Install the CLI extra in a Python project when you also need the command there:

```bash
pip install "banana-netcraze[cli]"
uv add "banana-netcraze[cli]"
```

## Quick Start

```python
from banana_netcraze.client import NetcrazeClient

with NetcrazeClient(
    url="http://192.168.1.1",
    username="admin",
    password="password",
) as client:
    version = client.get_version()
    interfaces = client.get_interfaces()
    devices = client.get_device_list()

print(version.title)
print(interfaces.keys())
print([device.ip for device in devices])
```

The client authenticates automatically when used as a context manager. Endpoint
methods also authenticate on demand and retry once if the router reports that
the session has expired.

## Client

```python
client = NetcrazeClient(
    url="http://192.168.1.1",
    username="admin",
    password="password",
    timeout=10.0,
)

client.auth()
version = client.get_version()
client.close()
```

`timeout` is passed to `httpx.Client`. Tests or advanced callers can also pass
an `httpx` transport through the `transport` argument.

## CLI

The package exposes the `banana-netcraze` command.

Download `startup-config.txt` and save it with the filename returned by the
router:

```bash
banana-netcraze startup-config \
  --url http://192.168.1.1 \
  --username admin \
  --password password
```

Write the startup config to stdout instead, so it can be piped or redirected:

```bash
banana-netcraze startup-config --password password --stdout > startup-config.txt
```

Download firmware:

```bash
banana-netcraze firmware --password password
```

## Supported Methods

| Method | Router endpoint | Return type |
| --- | --- | --- |
| `download_startup_config()` | `/ci/startup-config.txt` | `tuple[str, str]` |
| `download_firmware()` | `/ci/firmware` | `tuple[str, bytes]` |
| `get_version()` | `/rci/show/version` | `VersionModel` |
| `get_interfaces()` | `/rci/show/interface` | `dict[str, InterfaceModel]` |
| `get_interface(interface_name)` | `/rci/show/interface?name=...` | `InterfaceModel` |
| `get_device_list()` | `/rci/show/device-list` | `list[DeviceModel]` |
| `get_associations()` | `/rci/show/associations` | `list[AssociationStationModel]` |
| `get_arp()` | `/rci/show/ip/arp` | `list[DeviceModel]` |
| `get_hotspot()` | `/rci/show/ip/hotspot` | `list[DeviceModel]` |

## Response Models

Known response fields are parsed into Pydantic models from
`banana_netcraze.models`.

Router firmware can expose fields that are not modeled yet. Unknown fields are
kept in each model's `extra_fields` dictionary, and a warning is logged with
the field names and their runtime types. If you see that warning, please open
an issue so the missing fields can be added:

https://github.com/BananaLoaf/banana-netcraze/issues

## Development

Install dependencies with `uv`:

```bash
uv sync
```

Run linting:

```bash
uv run poe lint
```

Run type checks:

```bash
uv run poe typecheck
```

Run tests:

```bash
export TEST_USERNAME=admin
export TEST_PASSWORD=password
uv run poe test -q
```
