from datetime import UTC, datetime
from typing import NoReturn
from uuid import UUID, uuid4

from wdl_be_identity.domain.exceptions import InvariantViolationError


def new_entity_id() -> UUID:
    return uuid4()


def utc_now() -> datetime:
    return datetime.now(UTC)


def raise_invariant(dictionary_path: str, message_key: str) -> NoReturn:
    raise InvariantViolationError(message_key=f"{dictionary_path}.{message_key}")
