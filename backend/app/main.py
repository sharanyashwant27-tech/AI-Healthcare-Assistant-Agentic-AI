"""Shim so `uvicorn app.main:app` still works after the backend flatten."""

from main import app

__all__ = ["app"]
