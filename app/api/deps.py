from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from ..core.security import verify_token
from ..crud.user import get_user_by_email
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db

bearer_scheme = HTTPBearer()

async def get_current_user(token: str = Depends(bearer_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = verify_token(token.credentials)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
