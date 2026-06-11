import hashlib

import httpx
from loguru import logger

from banana_netcraze.models.device import DeviceModel
from banana_netcraze.models.interface import InterfaceModel
from banana_netcraze.models.version import VersionModel

AUTH_ENDPOINT = "/auth"
RCI_ENDPOINT = "/rci"
CI_ENDPOINT = "/ci"


class NetcrazeClient:
    def __init__(self, url: str, username: str, password: str):
        self.url = url.rstrip("/")
        self._session: None | httpx.Client = None

        self._username = username
        self._password = password

    @property
    def session(self) -> httpx.Client:
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(base_url=self.url)
        return self._session

    def __enter__(self):
        self.auth()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def auth(self):
        logger.info("Authenticating")

        res = self.session.get(AUTH_ENDPOINT)

        device = res.headers["X-NDM-Realm"]
        token = res.headers["X-NDM-Challenge"]

        digits = f"{self._username}:{device}:{self._password}"
        digits = hashlib.md5(digits.encode("utf-8")).hexdigest()
        digits = f"{token}{digits}"
        digits = hashlib.sha256(digits.encode("utf-8")).hexdigest()

        res = self.session.post(
            url=AUTH_ENDPOINT,
            json={"login": self._username, "password": digits},
        )
        res.raise_for_status()
        logger.success("Authentication successful")

    def close(self):
        self.session.close()
        self._session = None

    def download_startup_config(self) -> tuple[str, str]:
        logger.info("Downloading startup-config.txt")
        res = self.session.get(f"{CI_ENDPOINT}/startup-config.txt")
        res.raise_for_status()
        logger.success("Done!")
        return (
            res.headers["Content-Disposition"].split("filename=")[-1].strip('"'),
            res.content.decode(),
        )

    def download_firmware(self) -> tuple[str, bytes]:
        logger.info("Downloading firmware")
        res = self.session.get(f"{CI_ENDPOINT}/firmware")
        res.raise_for_status()
        logger.success("Done!")
        return (
            res.headers["Content-Disposition"].split("filename=")[-1].strip('"'),
            res.content,
        )

    def get_version(self) -> VersionModel:
        res = self.session.get(f"{RCI_ENDPOINT}/show/version")
        res.raise_for_status()
        return VersionModel(**res.json())

    def get_interfaces(self) -> dict[str, InterfaceModel]:
        res = self.session.get(f"{RCI_ENDPOINT}/show/interface")
        res.raise_for_status()
        return {
            name: InterfaceModel(**interface) for name, interface in res.json().items()
        }

    def get_interface(self, interface_name: str) -> InterfaceModel:
        res = self.session.get(f"{RCI_ENDPOINT}/show/interface?name={interface_name}")
        res.raise_for_status()
        return InterfaceModel(**res.json())

    def get_device_list(self) -> list[DeviceModel]:
        res = self.session.get(f"{RCI_ENDPOINT}/show/device-list")
        res.raise_for_status()
        return [DeviceModel(**device) for device in res.json()["host"]]

    def get_associations(self) -> dict:
        res = self.session.get(f"{RCI_ENDPOINT}/show/associations")
        res.raise_for_status()
        return res.json()

    def get_arp(self) -> list[DeviceModel]:
        res = self.session.get(f"{RCI_ENDPOINT}/show/ip/arp")
        res.raise_for_status()
        return [DeviceModel(**device) for device in res.json()]

    def get_hotspot(self) -> dict:
        res = self.session.get(f"{RCI_ENDPOINT}/show/ip/hotspot")
        res.raise_for_status()
        return res.json()
