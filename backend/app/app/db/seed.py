from sqlmodel.ext.asyncio.session import AsyncSession
from app import crud
from app.core.config import settings
from app.enums import IRoleEnum
from app.schemas.role_schema import IRoleCreate
from app.schemas.user_schema import IUserCreate

roles: list[IRoleCreate] = [
    IRoleCreate(name=IRoleEnum.admin.value, description="Администратор системы"),
    IRoleCreate(name=IRoleEnum.manager.value, description="Менеджер"),
    IRoleCreate(name=IRoleEnum.user.value, description="Пользователь"),
]

users: list[dict[str, str | IUserCreate]] = [
    {
        "data": IUserCreate(
            first_name="Admin",
            last_name="Test",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            is_superuser=True,
        ),
        "role": IRoleEnum.admin.value,
    },
    {
        "data": IUserCreate(
            first_name="Manager",
            last_name="Test",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="manager@example.com",
            is_superuser=False,
        ),
        "role": IRoleEnum.manager.value,
    },
    {
        "data": IUserCreate(
            first_name="User",
            last_name="Test",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="user@example.com",
            is_superuser=False,
        ),
        "role": IRoleEnum.user.value,
    },
]


async def seed_roles(db_session: AsyncSession) -> None:
    for role in roles:
        role_current = await crud.role.get_role_by_name(
            name=role.name, db_session=db_session
        )
        if not role_current:
            await crud.role.create(obj_in=role, db_session=db_session)


async def seed_users(db_session: AsyncSession) -> None:
    for user in users:
        current_user = await crud.user.get_by_email(
            email=user["data"].email, db_session=db_session
        )
        role = await crud.role.get_role_by_name(
            name=user["role"], db_session=db_session
        )
        if not current_user and role:
            user["data"].role_id = role.id
            await crud.user.create_with_role(obj_in=user["data"], db_session=db_session)


async def seed_db(db_session: AsyncSession) -> None:
    await seed_roles(db_session)
    await seed_users(db_session)
