from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.crud.base_crud import CRUDBase
from app.modules.tenders.tender_model import Tender, TenderStatusHistory
from app.enums import TenderStatus
from app.modules.tenders.tender_schema import ITenderCreate, ITenderUpdate


class CRUDTender(CRUDBase[Tender, ITenderCreate, ITenderUpdate]):
    async def create_with_history(
        self,
        *,
        obj_in: ITenderCreate,
        created_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> Tender:
        db_session = db_session or self.db.session
        db_obj = self.model.from_orm(obj_in)

        if created_by_id:
            db_obj.created_by_id = created_by_id

        db_session.add(db_obj)
        await db_session.flush()

        history_entry = TenderStatusHistory(
            tender_id=db_obj.id,
            old_status=None,
            new_status=db_obj.status,
            changed_by_id=created_by_id,
            reason="Тендер создан",
        )
        db_session.add(history_entry)

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update_status(
        self,
        *,
        tender: Tender,
        new_status: TenderStatus,
        reason: str,
        changed_by_id: UUID | str | None = None,
        db_session: AsyncSession | None = None,
    ) -> Tender:
        db_session = db_session or self.db.session

        old_status = tender.status
        tender.status = new_status

        history_entry = TenderStatusHistory(
            tender_id=tender.id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by_id,
            reason=reason,
        )

        db_session.add(tender)
        db_session.add(history_entry)

        await db_session.commit()
        await db_session.refresh(tender)
        return tender


class CRUDTenderStatusHistory(
    CRUDBase[TenderStatusHistory, TenderStatusHistory, TenderStatusHistory]
):
    async def get_history_by_tender_id(
        self, *, tender_id: UUID | str, db_session: AsyncSession | None = None
    ) -> list[TenderStatusHistory]:
        db_session = db_session or self.db.session
        response = await db_session.execute(
            select(TenderStatusHistory)
            .where(TenderStatusHistory.tender_id == tender_id)
            .order_by(TenderStatusHistory.created_at.asc())
        )
        return response.scalars().all()


tender = CRUDTender(Tender)
tender_status_history = CRUDTenderStatusHistory(TenderStatusHistory)
