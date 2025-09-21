from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from ..core.security import verify_firebase_token
from ..crud.user import User
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.user import UserCreate

bearer_scheme = HTTPBearer()

def get_current_user(token: str = Depends(bearer_scheme), db: Session = Depends(get_db)):
    try:
        decoded = verify_firebase_token(token.credentials)
        firebase_uid = decoded["uid"]
        email = decoded.get("email")

        # Check if user exists in DB
        db_user = User.get_user_by_uid(db, firebase_uid)
        if not db_user:
            new_user = UserCreate(firebase_uid=firebase_uid, email=email)
            db_user = User.create_user(db, new_user)

        return db_user
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )
