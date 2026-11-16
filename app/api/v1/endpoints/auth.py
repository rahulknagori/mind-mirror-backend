"""Cookie-based authentication.

Flow for the frontend (all requests with credentials included, e.g. fetch(..., { credentials: "include" })):
  1. POST /auth/login      -> sets access/refresh/csrf cookies, returns { user, csrf_token }
  2. Normal API calls      -> access cookie is sent automatically; POST/PUT/PATCH/DELETE must
                              also send the header  X-CSRF-Token: <csrf_token>
  3. On 401 from any call  -> POST /auth/refresh once, then retry; if refresh also returns 401,
                              send the user to the login page
  4. POST /auth/logout     -> clears the cookies
  After a page reload, GET /auth/csrf returns the current CSRF token and GET /auth/me the user.
"""
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....api.deps import get_current_user
from ....core.auth_cookies import (
    CSRF_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    clear_auth_cookies,
    set_auth_cookies,
    set_csrf_cookie,
)
from ....core.database import get_db
from ....core.exceptions import UnauthorizedError
from ....core.response import success_response
from ....core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    generate_csrf_token,
    verify_password,
    verify_token,
)
from ....crud.user import get_user_by_email

router = APIRouter()


def _start_session(response: Response, user) -> schemas.user.AuthSession:
    """Issue fresh access/refresh/CSRF tokens for user and set them as cookies."""
    claims = {"sub": user.email}
    csrf_token = generate_csrf_token()
    set_auth_cookies(
        response,
        access_token=create_access_token(claims),
        refresh_token=create_refresh_token(claims),
        csrf_token=csrf_token,
    )
    return schemas.user.AuthSession(
        user=schemas.user.UserOut.model_validate(user),
        csrf_token=csrf_token,
    )


@router.post("/login", response_model=schemas.response.SuccessResponse[schemas.user.AuthSession])
async def login(
    user_credentials: schemas.user.UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Log in and set the session cookies. The JWT is never returned in the body."""
    db_user = await get_user_by_email(db, email=user_credentials.email)
    if not db_user or not verify_password(user_credentials.password, db_user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")

    return success_response(
        data=_start_session(response, db_user),
        message="Login successful",
        request=request,
    )


@router.post("/refresh", response_model=schemas.response.SuccessResponse[schemas.user.AuthSession])
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a valid refresh cookie for new access/refresh/CSRF tokens (sliding session)."""
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("Session expired, please log in again")

    try:
        payload = verify_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
        email = payload.get("sub")
        if not email:
            raise Exception("Missing subject")
    except Exception:
        raise UnauthorizedError("Session expired, please log in again")

    db_user = await get_user_by_email(db, email=email)
    if db_user is None:
        raise UnauthorizedError("Session expired, please log in again")

    return success_response(
        data=_start_session(response, db_user),
        message="Session refreshed",
        request=request,
    )


@router.post("/logout", response_model=schemas.response.SuccessResponse[None])
async def logout(request: Request, response: Response):
    """Clear the session cookies."""
    clear_auth_cookies(response)
    return success_response(data=None, message="Logged out", request=request)


@router.get("/me", response_model=schemas.response.SuccessResponse[schemas.user.UserOut])
async def me(request: Request, current_user=Depends(get_current_user)):
    """Return the currently authenticated user."""
    return success_response(
        data=schemas.user.UserOut.model_validate(current_user),
        message="User retrieved successfully",
        request=request,
    )


@router.get("/csrf", response_model=schemas.response.SuccessResponse[schemas.user.CSRFToken])
async def csrf(request: Request, response: Response):
    """Return the current CSRF token (e.g. after a page reload), issuing one if missing."""
    token = request.cookies.get(CSRF_COOKIE_NAME)
    if not token:
        token = generate_csrf_token()
        set_csrf_cookie(response, token)
    return success_response(
        data=schemas.user.CSRFToken(csrf_token=token),
        message="CSRF token",
        request=request,
    )
