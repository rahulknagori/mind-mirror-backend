from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate

def get_user_by_uid(db: Session, firebase_uid: str):
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()

def create_user(db: Session, user_data: UserCreate):
    db_user = User(
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
        full_name=user_data.full_name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
