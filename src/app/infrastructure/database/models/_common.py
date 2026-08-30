from enum import Enum as PythonEnum

from sqlalchemy import Enum

from app.domain.enums import AccountStatus, AccountSubject


def _enum_values(enum: type[PythonEnum]) -> list[str]:
    return [str(member.value) for member in enum]


account_subject_type = Enum(
    AccountSubject,
    values_callable=_enum_values,
    native_enum=False,
    length=32,
    name="account_subject",
)
account_status_type = Enum(
    AccountStatus,
    values_callable=_enum_values,
    native_enum=False,
    length=32,
    name="account_status",
)
