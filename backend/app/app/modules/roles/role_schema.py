from app.modules.roles.role_model import RoleBase
from app.utils.partial import optional
from app.enums import IRoleEnum  # noqa: F401
from uuid import UUID


class IRoleCreate(RoleBase):
    pass


# All these fields are optional
@optional
class IRoleUpdate(RoleBase):
    pass


class IRoleRead(RoleBase):
    id: UUID
