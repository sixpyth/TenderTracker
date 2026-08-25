from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel, AutoString
from app.models.base_uuid_model import BaseUUIDModel
from app.enums import TenderStatus


class TenderBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = Field(default=None)
    status: TenderStatus = Field(
        default=TenderStatus.DRAFT, index=True, sa_type=AutoString
    )


class Tender(BaseUUIDModel, TenderBase, table=True):
    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Tender.created_by_id==User.id",
        }
    )
    status_history: list["TenderStatusHistory"] = Relationship(  # noqa: F821
        back_populates="tender",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )


class TenderStatusHistoryBase(SQLModel):
    tender_id: UUID = Field(foreign_key="Tender.id", index=True)
    old_status: TenderStatus | None = Field(default=None, sa_type=AutoString)
    new_status: TenderStatus = Field(..., sa_type=AutoString)
    reason: str = Field(...)


class TenderStatusHistory(BaseUUIDModel, TenderStatusHistoryBase, table=True):
    changed_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    changed_by: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "TenderStatusHistory.changed_by_id==User.id",
        }
    )
    tender: "Tender" = Relationship(  # noqa: F821
        back_populates="status_history",
        sa_relationship_kwargs={"lazy": "joined"},
    )
