from typing import Any

from pydantic import ConfigDict, field_validator

from banana_netcraze.models.base import AutoNoneBaseModel


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
    def convert_string_to_list(cls, v: Any) -> Any:
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
