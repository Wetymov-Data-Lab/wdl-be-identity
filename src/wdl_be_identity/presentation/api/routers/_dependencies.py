from typing import Annotated

from fastapi import Depends

from wdl_be_identity.application.passwords import PasswordHasher
from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.presentation.api.dependencies.passwords import get_password_hasher
from wdl_be_identity.presentation.api.dependencies.unit_of_work import get_account_uow

AccountUow = Annotated[UnitOfWork, Depends(get_account_uow)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
