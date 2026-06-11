from pydantic import ConfigDict

from banana_netcraze.models.base import AutoNoneBaseModel
from banana_netcraze.models.device import DeviceModel


class HotspotModel(AutoNoneBaseModel):
    model_config = ConfigDict(extra="forbid")

    host: list[DeviceModel]
