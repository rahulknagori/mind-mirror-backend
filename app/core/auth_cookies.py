"""Auth cookie names and helpers for setting/clearing them."""
from fastapi import Response
from .config import settings

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

# The refresh cookie is only sent to the auth endpoints, never to regular API calls.
REFRESH_COOKIE_PATH = "/api/v1/auth"


def _common_kwargs() -> dict:
    return {
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "domain": settings.COOKIE_DOMAIN,
    }


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
    common = _common_kwargs()
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        path="/",
        **common,
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        path=REFRESH_COOKIE_PATH,
        **common,
    )
    set_csrf_cookie(response, csrf_token)


def set_csrf_cookie(response: Response, csrf_token: str) -> None:
    # Not HttpOnly: when the frontend is on the same site (Vercel rewrite) its JS may
    # read it. The token is also returned in response bodies for cross-site setups.
    response.set_cookie(
        CSRF_COOKIE_NAME,
        csrf_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=False,
        path="/",
        **_common_kwargs(),
    )


def clear_auth_cookies(response: Response) -> None:
    common = _common_kwargs()
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/", httponly=True, **common)
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH, httponly=True, **common)
    response.delete_cookie(CSRF_COOKIE_NAME, path="/", **common)
