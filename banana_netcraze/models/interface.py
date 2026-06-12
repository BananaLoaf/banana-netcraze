from typing import Any

from pydantic import Field, field_validator

from banana_netcraze.models.base import AutoNoneBaseModel


class InterfacePortModel(AutoNoneBaseModel):
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
    address: str
    prefix_length: int = Field(alias="prefix-length")
    proto: str
    valid_lifetime: str = Field(alias="valid-lifetime")


class InterfaceBridgeModel(AutoNoneBaseModel):
    interface: str
    link: bool


class InterfaceModel(AutoNoneBaseModel):
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
    def convert_ipv6(cls, v: Any) -> Any:
        addresses = []

        if isinstance(v, dict) and v.get("addresses") is not None:
            for address in v["addresses"]:
                addresses.append(InterfaceIPV6Model(**address))

        return addresses

    @field_validator("bridge", mode="before")
    @classmethod
    def convert_bridge(cls, v: Any) -> Any:
        bridges = []

        if isinstance(v, dict) and v.get("interface") is not None:
            for bridge in v["interface"]:
                bridges.append(InterfaceBridgeModel(**bridge))
            return bridges

        return bridges

    @field_validator("encryption", mode="before")
    @classmethod
    def convert_string_to_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.split(",")
        return v

    @field_validator("port", mode="before")
    @classmethod
    def convert_port(cls, v: Any) -> Any:
        if isinstance(v, dict):
            if "1" in v:
                for interface_id, interface in v.items():
                    v[interface_id] = InterfacePortModel(**interface)
            else:
                v = InterfacePortModel(**v)
        return v
