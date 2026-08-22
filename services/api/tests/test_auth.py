from datetime import UTC, datetime
from uuid import uuid4

import bcrypt
import pytest
from fastapi import status
from sqlalchemy import delete, select

from app.core.permissions import PERMISSION_CATALOG
from app.db.models.audit_log import AuditLog
from app.db.models.organization import Organization
from app.db.models.organization_subscription import OrganizationSubscription
from app.db.models.permission import Permission
from app.db.models.role import Role
from app.db.models.role_permission import RolePermission
from app.db.models.subscription_plan import SubscriptionPlan
from app.db.models.user import User
from app.db.session import get_db
from app.main import app
from tests.conftest import TEST_ROLE_ID, TestSessionLocal, override_get_db


@pytest.mark.asyncio
async def test_register_creates_organization_and_user(client):
    email = f"new-admin-{uuid4().hex[:8]}@ledgeros.co"
    phone_number = f"9{uuid4().int % 10**9:09d}"

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme Finance",
            "full_name": "New Admin",
            "email": email,
            "phone_number": phone_number,
            "password": "StrongPass!123",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == email
    assert data["organization_name"] == "Acme Finance"
    assert data["role_name"] == "OWNER"

    async with TestSessionLocal() as db:
        permission_result = await db.execute(select(Permission).where(Permission.code == "bills.read"))
        assert permission_result.scalar_one_or_none() is not None

    async with TestSessionLocal() as db:
        audit_result = await db.execute(
            select(AuditLog).where(
                AuditLog.actor_user_id == data["id"],
                AuditLog.action == "USER_REGISTERED",
            )
        )
        assert audit_result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_login_returns_access_token(client):
    org_id = uuid4()
    role_id = uuid4()
    user_id = uuid4()
    permission_id = uuid4()
    email = f"admin-{org_id.hex[:8]}@ledgeros.co"

    async with TestSessionLocal() as db:
        existing_org = await db.get(Organization, org_id)
        if existing_org is None:
            db.add(
                Organization(
                    id=org_id,
                    name="Auth Test Organization",
                    gstin="27AUTHORG123",
                    is_active=True,
                )
            )

        existing_role = await db.get(Role, role_id)
        if existing_role is None:
            db.add(
                Role(
                    id=role_id,
                    organization_id=org_id,
                    name="Admin",
                    description="Administrator",
                    is_active=True,
                )
            )

        starter_plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == "starter"))
        if starter_plan is None:
            starter_plan = SubscriptionPlan(
                code="starter",
                name="Starter",
                max_devices=2,
                is_active=True,
            )
            db.add(starter_plan)
            await db.flush()

        existing_subscription = await db.scalar(
            select(OrganizationSubscription).where(OrganizationSubscription.organization_id == org_id)
        )
        if existing_subscription is None:
            db.add(
                OrganizationSubscription(
                    organization_id=org_id,
                    plan_id=starter_plan.id,
                    status="active",
                    starts_at=datetime.now(UTC),
                )
            )

        existing_permission = await db.execute(select(Permission).where(Permission.code == "auth.me"))
        permission_record = existing_permission.scalar_one_or_none()
        if permission_record is None:
            permission_record = Permission(
                id=permission_id,
                code="auth.me",
                description="View current user profile",
                category="auth",
            )
            db.add(permission_record)
            await db.flush()

        for permission_code in PERMISSION_CATALOG:
            permission_result = await db.execute(select(Permission).where(Permission.code == permission_code))
            catalog_permission = permission_result.scalar_one_or_none()
            if catalog_permission is None:
                description, category = PERMISSION_CATALOG[permission_code]
                catalog_permission = Permission(
                    code=permission_code,
                    description=description,
                    category=category,
                )
                db.add(catalog_permission)
                await db.flush()

            catalog_link = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == catalog_permission.id,
                )
            )
            if catalog_link.scalar_one_or_none() is None:
                db.add(
                    RolePermission(
                        role_id=role_id,
                        permission_id=catalog_permission.id,
                    )
                )

        existing_user = await db.get(User, user_id)
        if existing_user is None:
            db.add(
                User(
                    id=user_id,
                    organization_id=org_id,
                    role_id=role_id,
                    phone_number="9999999999",
                    full_name="Auth User",
                    email=email,
                    password_hash=bcrypt.hashpw(
                        b"StrongPass!123",
                        bcrypt.gensalt(),
                    ).decode("utf-8"),
                    is_active=True,
                )
            )

        await db.commit()

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = override_get_db

    try:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "StrongPass!123"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        assert data["access_token"]

        token = data["access_token"]
        protected = await client.get(
            "/api/v1/bills",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert protected.status_code == status.HTTP_200_OK

        me = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == status.HTTP_200_OK
        assert me.json()["email"] == email

        async with TestSessionLocal() as db:
            audit_result = await db.execute(
                select(AuditLog).where(
                    AuditLog.actor_user_id == str(user_id),
                    AuditLog.action == "LOGIN_SUCCEEDED",
                )
            )
            assert audit_result.scalar_one_or_none() is not None
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


@pytest.mark.asyncio
async def test_login_locks_account_after_repeated_failures(client):
    email = f"lockout-{uuid4().hex[:8]}@ledgeros.co"
    phone_number = f"9{uuid4().int % 10**9:09d}"
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Lockout Test Organization",
            "full_name": "Lockout User",
            "email": email,
            "phone_number": phone_number,
            "password": "StrongPass!123",
        },
    )
    assert registration.status_code == status.HTTP_201_CREATED

    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPass!123"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == ("Account temporarily locked. Try again later.")


@pytest.mark.asyncio
async def test_route_permission_is_enforced(client):
    async with TestSessionLocal() as db:
        permission_result = await db.execute(select(Permission.id).where(Permission.code == "bills.read"))
        permission_id = permission_result.scalar_one()
        await db.execute(
            delete(RolePermission).where(
                RolePermission.role_id == TEST_ROLE_ID,
                RolePermission.permission_id == permission_id,
            )
        )
        await db.commit()

    response = await client.get("/api/v1/bills")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_refresh_token_rotates_and_revokes_previous_token(client):
    email = f"refresh-{uuid4().hex[:8]}@ledgeros.co"
    phone_number = f"9{uuid4().int % 10**9:09d}"
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Refresh Test Organization",
            "full_name": "Refresh User",
            "email": email,
            "phone_number": phone_number,
            "password": "StrongPass!123",
        },
    )
    assert registration.status_code == status.HTTP_201_CREATED

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    first_refresh_token = login.json()["refresh_token"]

    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert refresh.status_code == status.HTTP_200_OK
    second_refresh_token = refresh.json()["refresh_token"]
    assert second_refresh_token != first_refresh_token

    reused = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert reused.status_code == status.HTTP_401_UNAUTHORIZED

    replacement = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": second_refresh_token},
    )
    assert replacement.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_password_reset_changes_password_and_revokes_sessions(client):
    email = f"reset-{uuid4().hex[:8]}@ledgeros.co"
    phone_number = f"9{uuid4().int % 10**9:09d}"
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Reset Test Organization",
            "full_name": "Reset User",
            "email": email,
            "phone_number": phone_number,
            "password": "StrongPass!123",
        },
    )
    assert registration.status_code == status.HTTP_201_CREATED

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    old_refresh_token = login.json()["refresh_token"]

    request = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": email},
    )
    assert request.status_code == status.HTTP_200_OK
    reset_token = request.json()["reset_token"]
    assert reset_token

    confirm = await client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": reset_token,
            "password": "NewStrongPass!123",
        },
    )
    assert confirm.status_code == status.HTTP_200_OK

    old_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass!123"},
    )
    assert old_login.status_code == status.HTTP_401_UNAUTHORIZED

    revoked_refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )
    assert revoked_refresh.status_code == status.HTTP_401_UNAUTHORIZED

    new_login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "NewStrongPass!123"},
    )
    assert new_login.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_subscription_limits_active_devices(client):
    email = f"devices-{uuid4().hex[:8]}@ledgeros.co"
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Device Test Organization",
            "full_name": "Device User",
            "email": email,
            "phone_number": f"9{uuid4().int % 10**9:09d}",
            "password": "StrongPass!123",
        },
    )
    assert registration.status_code == status.HTTP_201_CREATED

    for device_id in ("phone-1", "tablet-1"):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "identifier": email,
                "password": "StrongPass!123",
                "device_id": device_id,
                "device_name": device_id,
            },
        )
        assert response.status_code == status.HTTP_200_OK

    third_device = await client.post(
        "/api/v1/auth/login",
        json={
            "identifier": email,
            "password": "StrongPass!123",
            "device_id": "laptop-1",
        },
    )
    assert third_device.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Device limit reached" in third_device.json()["detail"]


@pytest.mark.asyncio
async def test_otp_send_and_verify(client):
    send_resp = await client.post(
        "/api/v1/auth/otp/send",
        json={"phone_number": "9876543210"},
    )
    assert send_resp.status_code == status.HTTP_200_OK
    assert send_resp.json()["test_otp"] == "123456"

    verify_resp = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone_number": "9876543210", "otp": "123456"},
    )
    assert verify_resp.status_code == status.HTTP_200_OK
    assert verify_resp.json()["verified"] is True


@pytest.mark.asyncio
async def test_google_login(client):
    response = await client.post(
        "/api/v1/auth/google",
        json={
            "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imdvb2dsZV91c2VyQGxlZGdlcm9zLmxvY2FsIn0.signature",
            "organization_name": "Google Shop",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
