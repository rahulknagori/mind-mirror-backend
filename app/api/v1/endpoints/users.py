from fastapi import APIRouter, Depends, HTTPException, status
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....core.security import verify_password, create_access_token
from ....crud.user import create_user, get_user_by_email
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/login", response_model=schemas.user.Token)
def login(user_credentials: schemas.user.UserLogin, db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token"""
    # Get user by email
    db_user = get_user_by_email(db, email=user_credentials.email)
    
    # Check if user exists
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=schemas.user.UserOut)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

@router.post("/", response_model=schemas.user.UserOut)
def create_user_endpoint(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db, user)