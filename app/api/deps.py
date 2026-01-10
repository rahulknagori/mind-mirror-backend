from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from ..core.security import verify_token
from ..crud.user import get_user_by_email
from sqlalchemy.orm import Session
from ..core.database import get_db

bearer_scheme = HTTPBearer()

def get_current_user(token: str = Depends(bearer_scheme), db: Session = Depends(get_db)):
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
    
    user = get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
