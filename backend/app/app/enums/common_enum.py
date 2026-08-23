from enum import Enum


class ModeEnum(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"
    testing = "testing"


class IOrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"
