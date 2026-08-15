class LedgerOSError(Exception):
    """Base exception for LedgerOS application errors."""


class NotFoundError(LedgerOSError):
    pass


class ValidationError(LedgerOSError):
    pass
