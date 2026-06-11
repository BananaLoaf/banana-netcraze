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

    @pytest.mark.skip
    def test_download_startup_config(self, client):
        filename, content = client.download_startup_config()
        assert isinstance(filename, str)
        assert isinstance(content, str)

    @pytest.mark.skip
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
