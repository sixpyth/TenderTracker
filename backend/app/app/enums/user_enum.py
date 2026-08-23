from enum import Enum


class IGenderEnum(str, Enum):
    female = "female"
    male = "male"
    other = "other"


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
