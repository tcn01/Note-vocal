import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import ALGORITHM
from app.repositories.user_repository import user_repository

logger = logging.getLogger(__name__)

settings = get_settings()

# Dùng HTTPBearer thay vì OAuth2PasswordBearer để Swagger UI
# hiển thị ô nhập token trực tiếp, không phải form username/password
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            logger.warning("JWT missing sub claim")
            raise credentials_exception
        user_id = int(sub)
    except JWTError as e:
        logger.warning("JWT decode failed: %s", e)
        raise credentials_exception

    user = await user_repository.get(db, user_id)
    if user is None:
        logger.warning("User from JWT not found: id=%s", user_id)
        raise credentials_exception

    return user
