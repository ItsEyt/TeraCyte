"""
core/teracyte_client.py
HTTP client for the upstream TeraCyte API. Handles auth (login, token refresh)
and data fetching (image, results, user info). Raises AuthError or UpstreamError
so callers never need to inspect raw HTTP responses.
"""
import logging
import os
import requests
from core.database import save_tokens, get_tokens, clear_tokens
from models.schemas import TokenResponse, ImageResponse, ResultsResponse, UserInfo

logger = logging.getLogger(__name__)
BASE_URL: str = os.getenv("TERACYTE_BASE_URL", "").rstrip("/")

class AuthError(Exception):
    """Raised for authentication-related issues, such as missing/invalid tokens or failed refresh attempts."""

class UpstreamError(Exception):
    """Raised for unexpected upstream errors."""
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(message)

#* Internal helpers *#

def _post(path: str, payload: dict) -> dict:
    response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
    if not response.ok:
        raise UpstreamError(response.status_code, response.text)
    return response.json()

def _authed_get(path: str) -> dict:
    """GET with Bearer token; retries once after refresh on 401"""
    access, _ = get_tokens()
    response = _get_with_token(path, access)

    if response.status_code == 401:
        logger.info("Access token expired, attempting refresh...")
        refresh = _do_refresh()
        response = _get_with_token(path, refresh)

    if not response.ok:
        raise UpstreamError(response.status_code, response.text)

    try:
        return response.json()
    except Exception as exc:
        raise UpstreamError(502, f"Malformed JSON from upstream: {exc}") from exc

def _get_with_token(path: str, token: str | None) -> requests.Response:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{BASE_URL}{path}", headers=headers, timeout=15)

def _do_refresh() -> str:
    """Exchange refresh token for a new access token. Raises AuthError on failure."""
    _, refresh = get_tokens()
    if not refresh:
        raise AuthError("No refresh token available")
    try:
        data = _post("/api/auth/refresh", {"refresh_token": refresh})
        response = TokenResponse(**data)
        save_tokens(response.access_token, response.refresh_token)
        logger.info("Token refreshed successfully")
        return response.access_token
    except UpstreamError as exc:
        clear_tokens()
        raise AuthError(f"Token refresh failed ({exc.status})") from exc

#* Public API *#

def login(username: str, password: str) -> TokenResponse:
    data = _post("/api/auth/login", {"username": username, "password": password})
    response = TokenResponse(**data)
    save_tokens(response.access_token, response.refresh_token)
    logger.info(f"User '{username}' logged in")
    return response

def get_me() -> UserInfo:
    data = _authed_get("/api/auth/me")
    return UserInfo(**data)

def get_image() -> ImageResponse:
    data = _authed_get("/api/image")
    return ImageResponse(**data)

def get_results() -> ResultsResponse:
    data = _authed_get("/api/results")
    return ResultsResponse(**data)
