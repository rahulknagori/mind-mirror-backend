"""CSRF protection for cookie-authenticated requests (double-submit token).

Any state-changing request (POST/PUT/PATCH/DELETE) that carries an auth cookie must
send an X-CSRF-Token header equal to the csrf_token cookie. Requests authenticated
only with an Authorization: Bearer header carry no ambient credentials, so they are
not subject to CSRF and are let through.
"""
import secrets
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .auth_cookies import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, CSRF_COOKIE_NAME, CSRF_HEADER_NAME
from .response import ErrorCode, error_response

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

# Login starts a new session (and sets a fresh CSRF token), so it can't require one.
CSRF_EXEMPT_PATHS = {"/api/v1/auth/login"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            request.method in SAFE_METHODS
            or request.url.path in CSRF_EXEMPT_PATHS
            or not (request.cookies.get(ACCESS_COOKIE_NAME) or request.cookies.get(REFRESH_COOKIE_NAME))
        ):
            return await call_next(request)

        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)
        if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
            body = error_response(
                code=ErrorCode.FORBIDDEN,
                message="CSRF token missing or invalid",
                request=request,
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=body.model_dump(mode="json", exclude_none=True),
            )

        return await call_next(request)
