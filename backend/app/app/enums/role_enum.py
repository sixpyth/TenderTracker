from enum import Enum


class IRoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"
