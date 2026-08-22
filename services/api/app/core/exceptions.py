from __future__ import annotations

from typing import Any


class LedgerOSError(Exception):
    """Base exception for LedgerOS application errors."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(LedgerOSError):
    """Raised when a business record is missing."""


class ValidationError(LedgerOSError):
    """Raised when business validation fails."""


class ConflictError(LedgerOSError):
    """Raised when a business rule is violated."""


class AuthenticationError(LedgerOSError):
    """Raised when authentication fails."""
