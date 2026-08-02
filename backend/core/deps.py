"""Compatibility shim — prefer ``auth.deps``."""

from auth.deps import CurrentUser, DbSession, get_current_user, require_roles

__all__ = ["CurrentUser", "DbSession", "get_current_user", "require_roles"]
