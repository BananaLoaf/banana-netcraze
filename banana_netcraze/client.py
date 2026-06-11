import hashlib
from typing import Any

import httpx
from loguru import logger

from banana_netcraze.models.association import AssociationStationModel
from banana_netcraze.models.device import DeviceModel
from banana_netcraze.models.interface import InterfaceModel
from banana_netcraze.models.version import VersionModel


class NetcrazeClient:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
    ):
        """Create a client for a Netcraze/Keenetic router.

        :param url: Base URL of the router web interface.
        :param username: Router account username.
        :param password: Router account password.
        :param timeout: Request timeout configuration passed to ``httpx.Client``.
        :param transport: Optional HTTP transport for tests or custom networking.
        """
        self.url = url.rstrip("/")
        self._session: None | httpx.Client = None
        self._is_authenticated = False
        self._timeout = timeout
        self._transport = transport

        self._username = username
        self._password = password

    @property
    def session(self) -> httpx.Client:
        """Return the underlying HTTP session, creating it if needed.

        :returns: Configured ``httpx.Client`` bound to the router base URL.
        """
        if self._session is None or self._session.is_closed:
            self._session = httpx.Client(
                base_url=self.url,
                timeout=self._timeout,
                transport=self._transport,
            )
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
        self._is_authenticated = False

        res = self.session.get("/auth")

        try:
            device = res.headers["X-NDM-Realm"]
            token = res.headers["X-NDM-Challenge"]
        except KeyError:
            res.raise_for_status()
            raise

        digits = f"{self._username}:{device}:{self._password}"
        digits = hashlib.md5(digits.encode("utf-8")).hexdigest()
        digits = f"{token}{digits}"
        digits = hashlib.sha256(digits.encode("utf-8")).hexdigest()

        res = self.session.post(
            url="/auth",
            json={"login": self._username, "password": digits},
        )
        res.raise_for_status()
        self._is_authenticated = True
        logger.success("Authentication successful")

    def close(self):
        """Close the underlying HTTP session."""
        if self._session is not None:
            self._session.close()
            self._session = None
        self._is_authenticated = False

    def _request(
        self,
        method: str,
        url: str,
        *,
        authenticate: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        if authenticate and not self._is_authenticated:
            self.auth()

        res = self.session.request(method, url, **kwargs)
        if authenticate and res.status_code in (401, 403):
            logger.info("Authentication expired, retrying")
            self.auth()
            res = self.session.request(method, url, **kwargs)

        res.raise_for_status()
        return res

    def _get(
        self,
        url: str,
        *,
        authenticate: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        return self._request("GET", url, authenticate=authenticate, **kwargs)

    def _get_json(
        self,
        url: str,
        *,
        authenticate: bool = True,
        **kwargs: Any,
    ) -> Any:
        return self._get(url, authenticate=authenticate, **kwargs).json()

    def download_startup_config(self) -> tuple[str, str]:
        """Download the router startup configuration.

        :returns: Tuple with the downloaded filename and decoded text content.
        :raises KeyError: If the response does not include a filename header.
        :raises httpx.HTTPStatusError: If the download request fails.
        """
        logger.info("Downloading startup-config.txt")
        res = self._get("/ci/startup-config.txt")
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
        res = self._get("/ci/firmware")
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
        return VersionModel.model_validate(self._get_json("/rci/show/version"))

    def get_interfaces(self) -> dict[str, InterfaceModel]:
        """Fetch all router network interfaces.

        :returns: Mapping of interface names to parsed interface models.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        data = self._get_json("/rci/show/interface")
        return {
            name: InterfaceModel.model_validate(interface)
            for name, interface in data.items()
        }

    def get_interface(self, interface_name: str) -> InterfaceModel:
        """Fetch a single router network interface by name.

        :param interface_name: Interface name or identifier accepted by the router.
        :returns: Parsed interface model.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        return InterfaceModel.model_validate(
            self._get_json(
                "/rci/show/interface",
                params={"name": interface_name},
            )
        )

    def get_device_list(self) -> list[DeviceModel]:
        """Fetch hosts known to the router device list.

        :returns: Parsed device models from ``show/device-list``.
        :raises KeyError: If the response does not include the ``host`` collection.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        data = self._get_json("/rci/show/device-list")
        return [DeviceModel.model_validate(device) for device in data.get("host", [])]

    def get_associations(self) -> list[AssociationStationModel]:
        """Fetch wireless station associations.

        :returns: Parsed wireless association stations.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        data = self._get_json("/rci/show/associations")
        return [
            AssociationStationModel.model_validate(station)
            for station in data.get("station", [])
        ]

    def get_arp(self) -> list[DeviceModel]:
        """Fetch the router ARP table.

        :returns: Parsed ARP entries as device models.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        data = self._get_json("/rci/show/ip/arp")
        return [DeviceModel.model_validate(device) for device in data]

    def get_hotspot(self) -> list[DeviceModel]:
        """Fetch hotspot host information.

        :returns: Parsed hotspot hosts.
        :raises httpx.HTTPStatusError: If the request fails.
        :raises pydantic.ValidationError: If the router response cannot be parsed.
        """
        data = self._get_json("/rci/show/ip/hotspot")
        return [DeviceModel.model_validate(host) for host in data.get("host", [])]
