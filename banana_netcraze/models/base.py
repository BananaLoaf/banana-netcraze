from typing import Any, ClassVar, Optional

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import PydanticUndefinedType


class AutoNoneBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    ISSUES_URL: ClassVar[str] = "https://github.com/BananaLoaf/banana-netcraze/issues"

    extra_fields: dict[str, Any] = Field(default_factory=dict)

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

    def model_post_init(self, __context: Any) -> None:
        extra_fields = self.__pydantic_extra__ or {}
        if not extra_fields:
            return

        object.__setattr__(self, "extra_fields", dict(extra_fields))
        object.__setattr__(self, "__pydantic_extra__", {})
        extra_fields_info = ", ".join(
            f"{key} ({type(value).__name__})"
            for key, value in sorted(extra_fields.items())
        )
        logger.warning(
            "Unexpected fields in {}: {}. Please open a GitHub issue here so "
            "the missing model fields can be added: {}",
            self.__class__.__name__,
            extra_fields_info,
            self.ISSUES_URL,
        )
