from fastapi import APIRouter, Depends, Request
from .... import schemas
from ....api.deps import get_current_user
from ....core.database import get_db
from ....core.security import verify_password, create_access_token
from ....core.response import success_response
from ....core.exceptions import UnauthorizedError, ConflictError
from ....crud.user import create_user, get_user_by_email
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/login", response_model=schemas.response.SuccessResponse[schemas.user.Token])
async def login(
    user_credentials: schemas.user.UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login endpoint - returns JWT token"""
    # Get user by email
    db_user = await get_user_by_email(db, email=user_credentials.email)
    
    # Check if user exists
    if not db_user:
        raise UnauthorizedError("Incorrect email or password")
    
    # Verify password
    if not verify_password(user_credentials.password, db_user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.email})
    
    token_data = schemas.user.Token(
        access_token=access_token,
        token_type="bearer"
    )
    
    return success_response(
        data=token_data,
        message="Login successful",
        request=request
    )

@router.get("/me", response_model=schemas.response.SuccessResponse[schemas.user.UserOut])
async def read_current_user(
    request: Request,
    current_user = Depends(get_current_user)
):
    user_out = schemas.user.UserOut.model_validate(current_user)
    return success_response(
        data=user_out,
        message="User retrieved successfully",
        request=request
    )

@router.post("/", response_model=schemas.response.SuccessResponse[schemas.user.UserOut])
async def create_user_endpoint(
    user: schemas.user.UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise ConflictError("Email already registered")
    
    created_user = await create_user(db, user)
    user_out = schemas.user.UserOut.model_validate(created_user)
    return success_response(
        data=user_out,
        message="User created successfully",
        request=request
    )