from typing import Any, Optional

from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType


class AutoNoneBaseModel(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        for field_info in cls.model_fields.values():
            if (
                isinstance(field_info.default, PydanticUndefinedType)
                and field_info.default_factory is None
            ):
                field_info.annotation = Optional[field_info.annotation]  # type: ignore[assignment]
                field_info.default = None

        cls.model_rebuild(force=True)
