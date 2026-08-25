from uuid import UUID
from app.utils.uuid6 import uuid7
from pydantic import BaseModel, field_validator
from app.modules.roles.role_schema import IRoleRead
from app.enums import IGenderEnum, IOrderEnum, TokenType  # noqa: F401


class IMetaGeneral(BaseModel):
    roles: list[IRoleRead]


class IUserMessage(BaseModel):
    """User message schema."""

    user_id: UUID | None
    message: str


class IChatResponse(BaseModel):
    """Chat response schema."""

    id: str
    message_id: str
    sender: str
    message: str
    type: str

    @field_validator("id", "message_id", mode="before")
    @classmethod
    def check_ids(cls, v):
        if v == "" or v is None:
            return str(uuid7())
        return v

    @field_validator("sender")
    @classmethod
    def sender_must_be_bot_or_you(cls, v):
        if v not in ["bot", "you"]:
            raise ValueError("sender must be bot or you")
        return v

    @field_validator("type")
    @classmethod
    def validate_message_type(cls, v):
        if v not in ["start", "stream", "end", "error", "info"]:
            raise ValueError("type must be start, stream or end")
        return v
