from typing import Annotated

from fastapi import Depends

from app.application.passwords import PasswordHasher
from app.application.unit_of_work import UnitOfWork
from app.presentation.api.dependencies.passwords import get_password_hasher
from app.presentation.api.dependencies.unit_of_work import get_account_uow

AccountUow = Annotated[UnitOfWork, Depends(get_account_uow)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
