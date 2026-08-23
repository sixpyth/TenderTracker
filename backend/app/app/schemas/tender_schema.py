from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.tender_model import TenderBase
from app.enums import TenderStatus
from app.utils.partial import optional


class ITenderCreate(TenderBase):
    pass


@optional
class ITenderUpdate(TenderBase):
    pass


class ITenderUpdateStatus(BaseModel):
    new_status: TenderStatus = Field(..., description="Новый статус тендера")
    reason: str = Field(..., min_length=1, description="Причина/комментарий изменения статуса")


class ITenderStatusHistoryRead(BaseModel):
    id: UUID
    tender_id: UUID
    old_status: TenderStatus | None = None
    new_status: TenderStatus
    changed_by_id: UUID | None = None
    reason: str
    created_at: datetime | None = None

    class Config:
        orm_mode = True


class ITenderRead(TenderBase):
    id: UUID
    created_by_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class ITenderReadWithHistory(ITenderRead):
    status_history: list[ITenderStatusHistoryRead] = []
