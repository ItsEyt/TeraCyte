"""
api/auth.py
Authentication endpoints: login, token refresh, current user, and logout.
Delegates all token management and upstream calls to teracyte_client.
"""
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from core import teracyte_client as client
from core.database import clear_tokens
from core.teracyte_client import AuthError, UpstreamError, _do_refresh
from models.schemas import LoginRequest

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/login")
def login():
    try:
        body = LoginRequest(**request.get_json(force=True))
        client.login(body.username, body.password)
        return jsonify({"message": "Logged in successfully"}), 200
    except (ValidationError, TypeError) as exc:
        return jsonify({"error": "Invalid request body", "detail": str(exc)}), 400
    except UpstreamError as exc:
        return jsonify({"error": "Login failed", "detail": str(exc)}), exc.status
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@auth_bp.post("/refresh")
def refresh():
    try:
        _do_refresh()
        return jsonify({"message": "Token refreshed"}), 200
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 401
    except UpstreamError as exc:
        return jsonify({"error": str(exc)}), exc.status


@auth_bp.get("/me")
def me():
    try:
        user = client.get_me()
        return jsonify(user.model_dump()), 200
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 401
    except UpstreamError as exc:
        return jsonify({"error": str(exc)}), exc.status


@auth_bp.post("/logout")
def logout():
    clear_tokens()
    return jsonify({"message": "Logged out"}), 200
