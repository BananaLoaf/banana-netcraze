import httpx
import pytest

from banana_netcraze.client import NetcrazeClient
from banana_netcraze.models.association import (
    AssociationsModel,
    AssociationStationModel,
)
from banana_netcraze.models.device import DeviceModel
from banana_netcraze.models.hotspot import HotspotModel
from banana_netcraze.models.interface import InterfaceModel
from banana_netcraze.models.version import VersionModel


def test_auth_accepts_challenge_response():
    requests = []

    def handler(request):
        requests.append(request)
        if request.method == "GET" and request.url.path == "/auth":
            # The router starts auth with a 401 challenge containing these headers.
            return httpx.Response(
                401,
                headers={
                    "X-NDM-Realm": "router",
                    "X-NDM-Challenge": "challenge",
                },
            )
        if request.method == "POST" and request.url.path == "/auth":
            # Posting the hashed challenge response completes authentication.
            return httpx.Response(200)
        return httpx.Response(404)

    client = NetcrazeClient(
        url="http://router.local",
        username="user",
        password="password",
        transport=httpx.MockTransport(handler),
    )

    client.auth()

    assert [request.method for request in requests] == ["GET", "POST"]


def test_auth_raises_status_without_challenge_headers():
    client = NetcrazeClient(
        url="http://router.local",
        username="user",
        password="password",
        transport=httpx.MockTransport(lambda request: httpx.Response(500)),
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.auth()


def test_request_reauthenticates_once_after_unauthorized():
    protected_calls = 0

    def handler(request):
        nonlocal protected_calls
        if request.method == "GET" and request.url.path == "/auth":
            # First step of auth: return the challenge headers.
            return httpx.Response(
                401,
                headers={
                    "X-NDM-Realm": "router",
                    "X-NDM-Challenge": "challenge",
                },
            )
        if request.method == "POST" and request.url.path == "/auth":
            # Second step of auth: accept the calculated credentials.
            return httpx.Response(200)
        if request.url.path == "/protected":
            protected_calls += 1
            if protected_calls == 1:
                # Simulate an expired session so the client re-authenticates once.
                return httpx.Response(403)
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(404)

    client = NetcrazeClient(
        url="http://router.local",
        username="user",
        password="password",
        transport=httpx.MockTransport(handler),
    )

    assert client._get_json("/protected") == {"ok": True}
    assert protected_calls == 2


class TestAPI:
    @pytest.fixture(scope="function")
    def blank_client(self, credentials):
        return NetcrazeClient(
            url="http://192.168.1.1/",
            username=credentials["username"],
            password=credentials["password"],
        )

    @pytest.fixture(scope="function")
    def client(self, blank_client):
        blank_client.auth()
        return blank_client

    def test_auth(self, blank_client):
        blank_client.auth()

    def test_auth_contextmanager(self, blank_client):
        with blank_client:
            pass

    def test_download_startup_config(self, client):
        filename, content = client.download_startup_config()
        assert isinstance(filename, str)
        assert isinstance(content, str)

    def test_download_firmware(self, client):
        filename, content = client.download_firmware()
        assert isinstance(filename, str)
        assert isinstance(content, bytes)

    def test_get_version(self, client):
        res = client.get_version()
        assert isinstance(res, VersionModel)

    def test_get_interfaces(self, client):
        res = client.get_interfaces()
        assert isinstance(res, dict)
        for interface_id, interface in res.items():
            assert isinstance(interface_id, str)
            assert isinstance(interface, InterfaceModel)

    def test_get_interface(self, client):
        res = client.get_interface(interface_name="1")
        assert isinstance(res, InterfaceModel)

    def test_get_device_list(self, client):
        res = client.get_device_list()
        assert isinstance(res, list)
        for dev in res:
            assert isinstance(dev, DeviceModel)

    def test_get_arp(self, client):
        res = client.get_arp()
        assert isinstance(res, list)
        for dev in res:
            assert isinstance(dev, DeviceModel)

    def test_get_associations(self, client):
        res = client.get_associations()
        assert isinstance(res, AssociationsModel)
        for station in res.station:
            assert isinstance(station, AssociationStationModel)

    def test_get_hotspot(self, client):
        res = client.get_hotspot()
        assert isinstance(res, HotspotModel)
        for host in res.host:
            assert isinstance(host, DeviceModel)
