import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: Optional[str], default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _as_list(value: Optional[str], default: List[str]) -> List[str]:
    if not value:
        return default
    return [item.strip().rstrip("/") for item in value.split(",") if item.strip()]


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # Session lifetimes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 7)

    # Comma-separated list of frontend origins allowed to send credentialed requests,
    # e.g. "https://my-app.vercel.app,http://localhost:5173"
    FRONTEND_ORIGINS: List[str] = _as_list(
        os.getenv("FRONTEND_ORIGINS"),
        ["http://localhost:3000", "http://localhost:5173"],
    )

    # Cookie settings.
    # - Frontend proxies /api to this backend (Vercel rewrite) -> COOKIE_SAMESITE=lax (default)
    # - Frontend calls this backend directly from another site   -> COOKIE_SAMESITE=none
    #   (requires COOKIE_SECURE=true; Safari blocks these third-party cookies)
    COOKIE_SECURE: bool = _as_bool(os.getenv("COOKIE_SECURE"), True)
    COOKIE_SAMESITE: str = (os.getenv("COOKIE_SAMESITE") or "lax").lower()
    COOKIE_DOMAIN: Optional[str] = os.getenv("COOKIE_DOMAIN") or None


settings = Settings()

if settings.COOKIE_SAMESITE not in ("lax", "strict", "none"):
    raise ValueError("COOKIE_SAMESITE must be one of: lax, strict, none")
if settings.COOKIE_SAMESITE == "none" and not settings.COOKIE_SECURE:
    raise ValueError("COOKIE_SAMESITE=none requires COOKIE_SECURE=true")
