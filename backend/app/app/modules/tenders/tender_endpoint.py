from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Params
from app import crud
from app.api import deps
from app.modules.tenders.tender_model import Tender
from app.modules.users.user_model import User
from app.schemas.common_schema import IOrderEnum
from app.modules.tenders.tender_schema import (
    ITenderCreate,
    ITenderRead,
    ITenderReadWithHistory,
    ITenderStatusHistoryRead,
    ITenderUpdateStatus,
)
from app.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.utils.exceptions.common_exception import IdNotFoundException

router = APIRouter()


@router.post("", response_model=IPostResponseBase[ITenderRead])
async def create_tender(
    tender_in: ITenderCreate,
    current_user: User = Depends(deps.get_current_user()),
) -> IPostResponseBase[ITenderRead]:
    """
    Создание нового тендера и логирование его начального статуса в историю
    """
    tender_obj = await crud.tender.create_with_history(
        obj_in=tender_in, created_by_id=current_user.id
    )
    return create_response(data=tender_obj, message="Тендер успешно создан")


@router.get("", response_model=IGetResponsePaginated[ITenderRead])
async def get_tender_list(
    params: Params = Depends(),
    order: IOrderEnum | None = Query(
        default=IOrderEnum.descendent, description="Сортировка по дате создания"
    ),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[ITenderRead]:
    """
    Получение пагинированного списка тендеров
    """
    tenders = await crud.tender.get_multi_paginated_ordered(
        params=params, order_by="created_at", order=order
    )
    return create_response(data=tenders)


@router.get("/{tender_id}", response_model=IGetResponseBase[ITenderReadWithHistory])
async def get_tender_by_id(
    tender_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[ITenderReadWithHistory]:
    """
    Получение тендера по ID вместе с историей изменения статусов
    """
    tender_obj = await crud.tender.get(id=tender_id)
    if not tender_obj:
        raise IdNotFoundException(Tender, tender_id)
    return create_response(data=tender_obj)


@router.patch("/{tender_id}/status", response_model=IPutResponseBase[ITenderRead])
async def update_tender_status(
    tender_id: UUID,
    status_update: ITenderUpdateStatus,
    current_user: User = Depends(deps.get_current_user()),
) -> IPutResponseBase[ITenderRead]:
    """
    Обновление статуса тендера (Черновик, Активен, Выигран, Проигран)
    с логированием (кто изменил, когда и почему) в историю.
    """
    tender_obj = await crud.tender.get(id=tender_id)
    if not tender_obj:
        raise IdNotFoundException(Tender, tender_id)

    updated_tender = await crud.tender.update_status(
        tender=tender_obj,
        new_status=status_update.new_status,
        reason=status_update.reason,
        changed_by_id=current_user.id,
    )
    return create_response(
        data=updated_tender, message="Статус тендера успешно обновлен"
    )


@router.get(
    "/{tender_id}/history",
    response_model=IGetResponseBase[list[ITenderStatusHistoryRead]],
)
async def get_tender_history(
    tender_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[list[ITenderStatusHistoryRead]]:
    """
    Получение подробной истории изменений статуса для конкретного тендера
    """
    tender_obj = await crud.tender.get(id=tender_id)
    if not tender_obj:
        raise IdNotFoundException(Tender, tender_id)

    history = await crud.tender_status_history.get_history_by_tender_id(
        tender_id=tender_id
    )
    return create_response(data=history)
