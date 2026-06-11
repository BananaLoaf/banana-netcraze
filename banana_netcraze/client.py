import hashlib

import httpx
from loguru import logger

from banana_netcraze.models.association import AssociationsModel
from banana_netcraze.models.device import DeviceModel
from banana_netcraze.models.hotspot import HotspotModel
from banana_netcraze.models.interface import InterfaceModel
from banana_netcraze.models.version import VersionModel

AUTH_ENDPOINT = "/auth"
RCI_ENDPOINT = "/rci"
CI_ENDPOINT = "/ci"


class NetcrazeClient:
    def __init__(self, url: str, username: str, password: str):
        """Create a client for a Netcraze/Keenetic router.

        :param url: Base URL of the router web interface.
        :param username: Router account username.
        :param password: Router account password.
        """
        self.url = url.rstrip("/")
        self._session: None | httpx.Client = None

        self._username = username
        self._password = password

    @property
    def session(self) -> httpx.Client:
        """Return the underlying HTTP session, creating it if needed.

        :returns: Configured ``httpx.Client`` bound to the router base URL.
        """
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(base_url=self.url)
        return self._session

    def __enter__(self):
        """Authenticate and enter the client context manager.

        :returns: The authenticated client instance.
        :raises httpx.HTTPStatusError: If authentication fails.
        """
        self.auth()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the HTTP session when leaving the context manager.

        :param exc_type: Exception type raised inside the context, if any.
        :param exc_val: Exception value raised inside the context, if any.
        :param exc_tb: Exception traceback raised inside the context, if any.
        """
        self.close()

    def auth(self):
        """Authenticate the current session with the router.

        :raises KeyError: If the router authentication challenge headers are missing.
        :raises httpx.HTTPStatusError: If the router rejects authentication.
        """
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
        """Close the underlying HTTP session."""
        self.session.close()
        self._session = None

    def download_startup_config(self) -> tuple[str, str]:
        """Download the router startup configuration.

        :returns: Tuple with the downloaded filename and decoded text content.
        :raises KeyError: If the response does not include a filename header.
        :raises httpx.HTTPStatusError: If the download request fails.
        """
        logger.info("Downloading startup-config.txt")
        res = self.session.get(f"{CI_ENDPOINT}/startup-config.txt")
        res.raise_for_status()
        logger.success("Done!")
        return (
            res.headers["Content-Disposition"].split("filename=")[-1].strip('"'),
            res.content.decode(),
        )

    def download_firmware(self) -> tuple[str, bytes]:
        """Download the router firmware image.

        :returns: Tuple with the downloaded filename and raw firmware bytes.
        :raises KeyError: If the response does not include a filename header.
        :raises httpx.HTTPStatusError: If the download request fails.
        """
        logger.info("Downloading firmware")
        res = self.session.get(f"{CI_ENDPOINT}/firmware")
        res.raise_for_status()
        logger.success("Done!")
        return (
            res.headers["Content-Disposition"].split("filename=")[-1].strip('"'),
            res.content,
        )

    def get_version(self) -> VersionModel:
        """Fetch router firmware and hardware version information.

        :returns: Parsed version information.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/version")
        res.raise_for_status()
        return VersionModel(**res.json())

    def get_interfaces(self) -> dict[str, InterfaceModel]:
        """Fetch all router network interfaces.

        :returns: Mapping of interface names to parsed interface models.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/interface")
        res.raise_for_status()
        return {
            name: InterfaceModel(**interface) for name, interface in res.json().items()
        }

    def get_interface(self, interface_name: str) -> InterfaceModel:
        """Fetch a single router network interface by name.

        :param interface_name: Interface name or identifier accepted by the router.
        :returns: Parsed interface model.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/interface?name={interface_name}")
        res.raise_for_status()
        return InterfaceModel(**res.json())

    def get_device_list(self) -> list[DeviceModel]:
        """Fetch hosts known to the router device list.

        :returns: Parsed device models from ``show/device-list``.
        :raises KeyError: If the response does not include the ``host`` collection.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/device-list")
        res.raise_for_status()
        return [DeviceModel(**device) for device in res.json()["host"]]

    def get_associations(self) -> AssociationsModel:
        """Fetch wireless station associations.

        :returns: Parsed wireless association data.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/associations")
        res.raise_for_status()
        return AssociationsModel(**res.json())

    def get_arp(self) -> list[DeviceModel]:
        """Fetch the router ARP table.

        :returns: Parsed ARP entries as device models.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/ip/arp")
        res.raise_for_status()
        return [DeviceModel(**device) for device in res.json()]

    def get_hotspot(self) -> HotspotModel:
        """Fetch hotspot host information.

        :returns: Parsed hotspot host data.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        res = self.session.get(f"{RCI_ENDPOINT}/show/ip/hotspot")
        res.raise_for_status()
        return HotspotModel(**res.json())
