from typing import Annotated

from fastapi import Depends

from app.application.passwords import PasswordHasher
from app.application.revocations import SessionRevocationStore
from app.application.tokens import TokenCodec
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account
from app.presentation.api.dependencies.authentication import get_access_token, get_current_account
from app.presentation.api.dependencies.passwords import get_password_hasher
from app.presentation.api.dependencies.revocations import get_session_revocation_store
from app.presentation.api.dependencies.tokens import get_token_codec
from app.presentation.api.dependencies.unit_of_work import get_account_uow

AccountUow = Annotated[UnitOfWork, Depends(get_account_uow)]
AccessToken = Annotated[str, Depends(get_access_token)]
CurrentAccount = Annotated[Account, Depends(get_current_account)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
SessionRevocationStoreDep = Annotated[SessionRevocationStore, Depends(get_session_revocation_store)]
TokenCodecDep = Annotated[TokenCodec, Depends(get_token_codec)]
