from pydantic import ConfigDict, Field

from banana_netcraze.models.base import AutoNoneBaseModel


class AssociationStationModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    mac: str
    ap: str
    psm: bool
    authenticated: bool
    txrate: int
    rxrate: int
    uptime: int
    txbytes: int
    rxbytes: int
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
    dl_mu: bool = Field(alias="dl-mu")
    ul_mu: bool = Field(alias="ul-mu")
    dl_ofdma: bool = Field(alias="dl-ofdma")
    ul_ofdma: bool = Field(alias="ul-ofdma")


class AssociationsModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    station: list[AssociationStationModel]
