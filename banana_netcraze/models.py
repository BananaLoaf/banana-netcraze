from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticUndefinedType


class AutoNoneBaseModel(BaseModel):
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     for field_name, field_info in cls.model_fields.items():
    #         if field_info.default is None and field_info.default_factory is None:
    #             field_info.default = None

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        for field_name, field_info in list(cls.model_fields.items()):
            if (
                isinstance(field_info.default, PydanticUndefinedType)
                and field_info.default_factory is None
            ):
                field_info.annotation = Optional[field_info.annotation]
                field_info.default = None

        cls.model_rebuild(force=True)

    # @model_validator(mode='before')
    # @classmethod
    # def set_missing_to_none(cls, data: Any) -> Any:
    #     if isinstance(data, dict):
    #         for field_name, field_info in cls.model_fields.items():
    #             if isinstance(field_info.default, PydanticUndefinedType) and field_info.default_factory is None:
    #                 field_info.annotation = Optional[field_info.annotation]
    #                 field_info.default = None
    #     return data


class NDMModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    exact: str
    cdate: str


class BSPModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    exact: str
    cdate: str


class NDWModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    features: list[str]
    components: list[str]

    @field_validator("features", "components", mode="before")
    @classmethod
    def convert_string_to_list(cls, v: any) -> any:
        if isinstance(v, str):
            return v.split(",")
        return v


class NDW3Model(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str


class NDW4Model(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str


class VersionModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    release: str
    sandbox: str
    title: str
    arch: str

    ndm: NDMModel
    bsp: BSPModel
    ndw: NDWModel
    ndw3: NDW3Model
    ndw4: NDW4Model

    manufacturer: str
    vendor: str
    series: str
    model: str
    hw_version: str
    hw_type: str
    hw_id: str
    device: str
    consent: str
    region: str
    description: str


class InterfacePortModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    index: int
    interface_name: str = Field(alias="interface-name")
    label: str
    type: str
    traits: list[str]
    link: str
    speed: str
    duplex: str
    auto_negotiation: str = Field(alias="auto-negotiation")
    flow_control: str = Field(alias="flow-control")
    eee: str

    last_change: str = Field(alias="last-change")
    last_overflow: str = Field(alias="last-overflow")
    cable_diagnostics: bool = Field(alias="cable-diagnostics")
    admin_only: bool = Field(alias="admin-only")
    public: bool
    link_group: dict = Field(alias="link-group")


class InterfaceIPV6Model(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str
    prefix_length: int = Field(alias="prefix-length")
    proto: str
    valid_lifetime: str = Field(alias="valid-lifetime")


class InterfaceBridgeModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    interface: str
    link: bool


class InterfaceModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    index: int
    interface_name: str = Field(alias="interface-name")
    type: str
    description: str
    traits: list[str]
    link: str
    connected: str
    state: str
    mtu: int
    tx_queue_length: int = Field(alias="tx-queue-length")
    admin_only: bool = Field(alias="admin-only")
    port: dict[str, InterfacePortModel] | InterfacePortModel
    summary: dict
    label: str
    last_change: str = Field(alias="last-change")
    last_overflow: str = Field(alias="last-overflow")
    cable_diagnostics: bool = Field(alias="cable-diagnostics")
    public: bool
    link_group: dict = Field(alias="link-group")
    speed: str
    duplex: str
    auto_negotiation: str = Field(alias="auto-negotiation")
    flow_control: str = Field(alias="flow-control")
    eee: str
    group: str
    usedby: list[str]
    ipv6: list[InterfaceIPV6Model]
    mac: str
    auth_type: str = Field(alias="auth-type")
    address: str
    mask: str
    uptime: int
    global_: bool = Field(alias="global")
    defaultgw: bool
    priority: int
    security_level: str = Field(alias="security-level")
    hwstate: str
    bitrate: int
    channel: int
    bandwidth: str
    busy_channels: list[int] = Field(alias="busy-channels")
    temperature: int
    ssid: str
    encryption: list[str]
    ap: str
    bridge: list[InterfaceBridgeModel]
    wireguard: dict

    @field_validator("ipv6", mode="before")
    @classmethod
    def convert_ipv6(cls, v: any) -> any:
        addresses = []

        if isinstance(v, dict) and v.get("addresses") is not None:
            for address in v["addresses"]:
                addresses.append(InterfaceIPV6Model(**address))

        return addresses

    @field_validator("bridge", mode="before")
    @classmethod
    def convert_bridge(cls, v: any) -> any:
        bridges = []

        if isinstance(v, dict) and v.get("interface") is not None:
            for bridge in v["interface"]:
                bridges.append(InterfaceBridgeModel(**bridge))
            return bridges

        return bridges

    # @field_validator("wireguard", mode="before")
    # @classmethod
    # def convert_wireguard(cls, v: any) -> any:
    #     return v

    @field_validator("encryption", mode="before")
    @classmethod
    def convert_string_to_list(cls, v: any) -> any:
        if isinstance(v, str):
            return v.split(",")
        return v

    @field_validator("port", mode="before")
    @classmethod
    def convert_port(cls, v: any) -> any:
        if isinstance(v, dict):
            if "1" in v:
                for interface_id, interface in v.items():
                    v[interface_id] = InterfacePortModel(**interface)
            else:
                v = InterfacePortModel(**v)
        return v


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
