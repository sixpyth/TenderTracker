from enum import Enum


class TenderStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
