"""Class to manage transaction types in Transaction Record."""

from enum import Enum


class TransactionTypes(Enum):
    """Represents roles in Connection Record."""

    SCHEMA = (1,)
    CREDENTIAL_DEFINITION = (2,)