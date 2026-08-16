from uuid import UUID

# Temporary development organization.
# This must be replaced by the authenticated user's organization
# once authentication is implemented.
DEVELOPMENT_ORGANIZATION_ID = UUID(
    "00000000-0000-0000-0000-000000000001"
)


async def get_current_organization_id() -> UUID:
    """
    Temporary development dependency.

    Returns a fixed organization ID until real authentication
    and user/organization resolution are implemented.
    """
    return DEVELOPMENT_ORGANIZATION_ID


async def get_current_user_id() -> UUID:
    """
    Temporary development dependency.

    Returns a fixed user ID until authentication is implemented.
    """
    return UUID("00000000-0000-0000-0000-000000000002")