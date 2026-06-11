from pydantic import ConfigDict, Field

from banana_netcraze.models.base import AutoNoneBaseModel


class DeviceInterfaceModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str


class DeviceDhcpModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    expires: int


class DeviceTrafficShapeModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    rx: int
    tx: int
    mode: str
    schedule: str


class DeviceModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    mac: str
    via: str
    ip: str
    hostname: str
    name: str
    state: str
    mws_backhaul: bool = Field(alias="mws-backhaul")
    interface: DeviceInterfaceModel | str
    dhcp: DeviceDhcpModel
    registered: bool
    access: str
    schedule: str
    priority: int
    active: bool
    rxbytes: int
    txbytes: int
    link: str
    ssid: str
    ap: str
    psm: bool
    mld: bool
    authenticated: bool
    txrate: int
    ht: int
    mode: str
    gi: int
    rssi: int
    mcs: int
    txss: int
    ebf: bool
    eleven: list[str] = Field(alias="_11")
    pmf: bool
    security: str
    uptime: int
    first_seen: int = Field(alias="first-seen")
    last_seen: int = Field(alias="last-seen")
    traffic_shape: DeviceTrafficShapeModel = Field(alias="traffic-shape")
    auto_negotiation: bool = Field(alias="auto-negotiation")
    speed: int
    duplex: bool
    port: str
    dl_ofdma: bool = Field(alias="dl-ofdma")
    dl_mu: bool = Field(alias="dl-mu")
