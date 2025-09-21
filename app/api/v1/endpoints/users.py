from fastapi import APIRouter, Depends
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....models.user import User
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/me", response_model=schemas.user.UserOut)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

@router.post("/", response_model=schemas.user.UserOut)
def create_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    return User.create_user(db, user)