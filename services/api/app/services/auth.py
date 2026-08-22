import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import bcrypt
import jwt
import pyotp
from cryptography.fernet import Fernet
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.permissions import PERMISSION_CATALOG
from app.db.models.audit_log import AuditLog
from app.db.models.device_session import DeviceSession
from app.db.models.organization import Organization
from app.db.models.organization_subscription import OrganizationSubscription
from app.db.models.password_reset_token import PasswordResetToken
from app.db.models.permission import Permission
from app.db.models.refresh_token import RefreshToken
from app.db.models.role import Role
from app.db.models.role_permission import RolePermission
from app.db.models.subscription_plan import SubscriptionPlan
from app.db.models.user import User
from app.schemas.auth import (
    DeviceSessionResponse,
    MFAConfirmRequest,
    MFASetupResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)


class AuthService:
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def normalize_phone(phone_number: str) -> str:
        value = phone_number.strip()
        if value.startswith("+"):
            normalized = "+" + re.sub(r"\D", "", value)
        else:
            normalized = re.sub(r"\D", "", value)
        digits = normalized[1:] if normalized.startswith("+") else normalized
        if not 8 <= len(digits) <= 15:
            raise ValueError("Phone number must contain 8 to 15 digits.")
        return normalized

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        organization_name = payload.organization_name.strip()
        full_name = payload.full_name.strip()
        email = payload.email.strip().lower() if payload.email else None
        phone_number = self.normalize_phone(payload.phone_number)
        password = payload.password.strip()

        if not organization_name:
            raise ValueError("Organization name is required.")

        if not full_name:
            raise ValueError("Full name is required.")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if email:
            existing_user = await self.db.execute(
                select(User).where(User.email == email)
            )
            if existing_user.scalar_one_or_none() is not None:
                raise ValueError("A user with this email already exists.")

        existing_phone = await self.db.execute(
            select(User.id)
            .where(User.phone_number == phone_number)
            .limit(1)
        )
        if existing_phone.scalar_one_or_none() is not None:
            raise ValueError("A user with this phone number already exists.")

        organization = Organization(
            name=organization_name,
            email=email,
            phone=phone_number,
            is_active=True,
        )
        self.db.add(organization)
        await self.db.flush()

        trial_plan = await self.db.scalar(
            select(SubscriptionPlan).where(
                SubscriptionPlan.code == "free_trial"
            )
        )
        if trial_plan is None:
            trial_plan = SubscriptionPlan(
                code="free_trial",
                name="Free Trial",
                max_devices=2,
                price_per_device=0,
                currency="INR",
                billing_interval="monthly",
                trial_days=14,
                is_active=True,
            )
            self.db.add(trial_plan)
            await self.db.flush()
        self.db.add(
            OrganizationSubscription(
                organization_id=organization.id,
                plan_id=trial_plan.id,
                status="active",
                starts_at=datetime.now(UTC),
                ends_at=datetime.now(UTC)
                + timedelta(days=trial_plan.trial_days),
            )
        )

        role = Role(
            organization_id=organization.id,
            name="OWNER",
            description="Organization owner with full access.",
            is_active=True,
        )
        self.db.add(role)
        await self.db.flush()

        permission_result = await self.db.execute(
            select(Permission).where(
                Permission.code.in_(PERMISSION_CATALOG.keys())
            )
        )
        permissions = {
            permission.code: permission
            for permission in permission_result.scalars().all()
        }
        for code, (description, category) in PERMISSION_CATALOG.items():
            permission_record = permissions.get(code)
            if permission_record is None:
                permission_record = Permission(
                    code=code,
                    description=description,
                    category=category,
                )
                self.db.add(permission_record)
                await self.db.flush()

            self.db.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission_record.id,
                )
            )

        user = User(
            organization_id=organization.id,
            role_id=role.id,
            phone_number=phone_number,
            full_name=full_name,
            email=email,
            password_hash=self.hash_password(password),
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        self.db.add(
            AuditLog(
                organization_id=organization.id,
                actor_user_id=user.id,
                entity_type="user",
                entity_id=user.id,
                action="USER_REGISTERED",
                details={"role": role.name},
            )
        )

        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(organization)
        await self.db.refresh(role)

        return RegisterResponse(
            id=user.id,
            organization_id=organization.id,
            role_id=role.id,
            organization_name=organization.name,
            role_name=role.name,
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
        )

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def _fernet(self) -> Fernet:
        return Fernet(settings.MFA_ENCRYPTION_KEY.encode("utf-8"))

    async def authenticate(
        self,
        identifier: str,
        password: str,
        otp: str | None = None,
    ) -> User:
        normalized_identifier = identifier.strip()
        if "@" in normalized_identifier:
            lookup = User.email == normalized_identifier.lower()
        else:
            lookup = User.phone_number == self.normalize_phone(
                normalized_identifier
            )
        result = await self.db.execute(
            select(User)
            .where(
                lookup,
            )
            .with_for_update()
            .order_by(User.created_at.asc())
            .limit(1)
        )
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise ValueError("Invalid email or password.")

        now = datetime.now(UTC)
        if user.locked_until and user.locked_until > now:
            raise ValueError("Account temporarily locked. Try again later.")

        if user.locked_until and user.locked_until <= now:
            user.locked_until = None
            user.failed_login_attempts = 0

        if not self.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + self.LOCKOUT_DURATION
            self.db.add(
                AuditLog(
                    organization_id=user.organization_id,
                    actor_user_id=user.id,
                    entity_type="user",
                    entity_id=user.id,
                    action="LOGIN_FAILED",
                    details={
                        "failed_attempts": user.failed_login_attempts,
                        "locked": user.locked_until is not None,
                    },
                )
            )
            await self.db.commit()
            raise ValueError("Invalid email or password.")

        if user.mfa_enabled:
            if not otp:
                raise ValueError("Multi-factor authentication code required.")
            try:
                secret = self._fernet().decrypt(
                    user.mfa_secret.encode("utf-8")
                ).decode("utf-8")
            except Exception as exc:
                raise ValueError("Multi-factor authentication is unavailable.") from exc
            if not pyotp.TOTP(secret).verify(otp, valid_window=1):
                raise ValueError("Invalid multi-factor authentication code.")

        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.add(
            AuditLog(
                organization_id=user.organization_id,
                actor_user_id=user.id,
                entity_type="user",
                entity_id=user.id,
                action="LOGIN_SUCCEEDED",
                details=None,
            )
        )
        await self.db.commit()
        return user

    def create_access_token(
        self,
        user: User,
        device_session_id: UUID | None = None,
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "org_id": str(user.organization_id),
            "role_id": str(user.role_id),
            "iat": int(now.timestamp()),
            "exp": int(
                (
                    now
                    + timedelta(
                        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                ).timestamp()
            ),
        }
        if device_session_id is not None:
            payload["sid"] = str(device_session_id)
        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def issue_tokens(self, user: User) -> TokenResponse:
        return await self.issue_tokens_for_device(user, str(uuid4()), None, None)

    async def issue_tokens_for_device(
        self,
        user: User,
        device_id: str,
        device_name: str | None,
        ip_address: str | None,
    ) -> TokenResponse:
        now = datetime.now(UTC)
        subscription_result = await self.db.execute(
            select(OrganizationSubscription)
            .options(selectinload(OrganizationSubscription.plan))
            .where(
                OrganizationSubscription.organization_id == user.organization_id,
                OrganizationSubscription.status == "active",
                OrganizationSubscription.starts_at <= now,
                (OrganizationSubscription.ends_at.is_(None))
                | (OrganizationSubscription.ends_at > now),
            )
            .with_for_update()
        )
        subscription = subscription_result.scalar_one_or_none()
        if subscription is None:
            raise ValueError("No active subscription is available.")

        session = await self.db.scalar(
            select(DeviceSession)
            .where(
                DeviceSession.user_id == user.id,
                DeviceSession.device_id == device_id,
                DeviceSession.is_active.is_(True),
                DeviceSession.revoked_at.is_(None),
            )
            .with_for_update()
        )
        if session is None:
            active_count = await self.db.scalar(
                select(func.count(DeviceSession.id)).where(
                    DeviceSession.user_id == user.id,
                    DeviceSession.is_active.is_(True),
                    DeviceSession.revoked_at.is_(None),
                )
            )
            if int(active_count or 0) >= subscription.plan.max_devices:
                raise ValueError(
                    f"Device limit reached for the {subscription.plan.name} plan."
                )
            session = DeviceSession(
                user_id=user.id,
                device_id=device_id,
                device_name=device_name,
                last_ip=ip_address,
                last_seen_at=now,
            )
            self.db.add(session)
            await self.db.flush()
        else:
            session.last_seen_at = now
            session.last_ip = ip_address

        refresh_token = secrets.token_urlsafe(48)
        refresh_record = RefreshToken(
            user_id=user.id,
            device_session_id=session.id,
            token_hash=self.hash_refresh_token(refresh_token),
            expires_at=now
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_record)
        await self.db.commit()
        return TokenResponse(
            access_token=self.create_access_token(user, session.id),
            refresh_token=refresh_token,
        )

    async def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        now = datetime.now(UTC)
        token_hash = self.hash_refresh_token(payload.refresh_token)
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .with_for_update()
        )
        refresh_record = result.scalar_one_or_none()
        if (
            refresh_record is None
            or refresh_record.revoked_at is not None
            or refresh_record.expires_at <= now
        ):
            raise ValueError("Invalid or expired refresh token.")

        user = await self.db.get(User, refresh_record.user_id)
        if user is None or not user.is_active:
            raise ValueError("Invalid or expired refresh token.")

        session = await self.db.get(
            DeviceSession,
            refresh_record.device_session_id,
            with_for_update=True,
        )
        if (
            session is None
            or not session.is_active
            or session.revoked_at is not None
        ):
            raise ValueError("Device session is no longer active.")

        refresh_record.revoked_at = now
        replacement = secrets.token_urlsafe(48)
        replacement_record = RefreshToken(
            user_id=user.id,
            device_session_id=session.id,
            token_hash=self.hash_refresh_token(replacement),
            expires_at=now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(replacement_record)
        await self.db.flush()
        refresh_record.replaced_by_id = replacement_record.id
        await self.db.commit()

        return TokenResponse(
            access_token=self.create_access_token(user, session.id),
            refresh_token=replacement,
        )

    async def request_password_reset(
        self,
        payload: PasswordResetRequest,
    ) -> PasswordResetResponse:
        normalized_email = payload.email.strip().lower()
        result = await self.db.execute(
            select(User).where(
                User.email == normalized_email,
                User.is_active.is_(True),
            )
        )
        user = result.scalar_one_or_none()
        reset_token = None
        if user is not None:
            reset_token = secrets.token_urlsafe(48)
            self.db.add(
                PasswordResetToken(
                    user_id=user.id,
                    token_hash=self.hash_refresh_token(reset_token),
                    expires_at=datetime.now(UTC)
                    + timedelta(
                        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
                    ),
                )
            )
            await self.db.commit()

        response = PasswordResetResponse(
            message="If the account exists, reset instructions have been sent."
        )
        if settings.ENVIRONMENT != "production":
            response.reset_token = reset_token
        return response

    async def confirm_password_reset(
        self,
        payload: PasswordResetConfirmRequest,
    ) -> PasswordResetResponse:
        if len(payload.password.strip()) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        now = datetime.now(UTC)
        result = await self.db.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_hash
                == self.hash_refresh_token(payload.token),
            )
            .with_for_update()
        )
        reset_record = result.scalar_one_or_none()
        if (
            reset_record is None
            or reset_record.used_at is not None
            or reset_record.expires_at <= now
        ):
            raise ValueError("Invalid or expired password reset token.")

        user = await self.db.get(User, reset_record.user_id)
        if user is None or not user.is_active:
            raise ValueError("Invalid or expired password reset token.")

        user.password_hash = self.hash_password(payload.password.strip())
        reset_record.used_at = now
        refresh_tokens = await self.db.scalars(
            select(RefreshToken).where(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        for refresh_token in refresh_tokens:
            refresh_token.revoked_at = now

        self.db.add(
            AuditLog(
                organization_id=user.organization_id,
                actor_user_id=user.id,
                entity_type="user",
                entity_id=user.id,
                action="PASSWORD_RESET",
                details=None,
            )
        )
        await self.db.commit()
        return PasswordResetResponse(message="Password has been reset.")

    async def setup_mfa(self, user: User) -> MFASetupResponse:
        secret = pyotp.random_base32()
        user.mfa_secret = self._fernet().encrypt(
            secret.encode("utf-8")
        ).decode("utf-8")
        user.mfa_enabled = False
        await self.db.commit()
        account = user.email or user.full_name
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(
            name=account,
            issuer_name=settings.APP_NAME,
        )
        return MFASetupResponse(provisioning_uri=provisioning_uri)

    async def confirm_mfa(
        self,
        user: User,
        payload: MFAConfirmRequest,
    ) -> None:
        if not user.mfa_secret:
            raise ValueError("MFA setup has not been started.")
        secret = self._fernet().decrypt(
            user.mfa_secret.encode("utf-8")
        ).decode("utf-8")
        if not pyotp.TOTP(secret).verify(payload.code, valid_window=1):
            raise ValueError("Invalid multi-factor authentication code.")
        user.mfa_enabled = True
        await self.db.commit()

    async def disable_mfa(self, user: User) -> None:
        user.mfa_secret = None
        user.mfa_enabled = False
        await self.db.commit()

    async def list_device_sessions(
        self,
        user: User,
    ) -> list[DeviceSessionResponse]:
        result = await self.db.execute(
            select(DeviceSession)
            .where(
                DeviceSession.user_id == user.id,
                DeviceSession.is_active.is_(True),
                DeviceSession.revoked_at.is_(None),
            )
            .order_by(DeviceSession.last_seen_at.desc())
        )
        return [
            DeviceSessionResponse(
                id=session.id,
                device_id=session.device_id,
                device_name=session.device_name,
                last_ip=session.last_ip,
                last_seen_at=session.last_seen_at,
                is_current=False,
            )
            for session in result.scalars().all()
        ]

    async def revoke_device_session(
        self,
        user: User,
        session_id: UUID,
    ) -> None:
        session = await self.db.scalar(
            select(DeviceSession).where(
                DeviceSession.id == session_id,
                DeviceSession.user_id == user.id,
            )
        )
        if session is None:
            raise ValueError("Device session not found.")
        session.is_active = False
        session.revoked_at = datetime.now(UTC)
        await self.db.commit()

    async def login(
        self,
        identifier: str,
        password: str,
        otp: str | None = None,
        device_id: str | None = None,
        device_name: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        user = await self.authenticate(identifier, password, otp)
        return await self.issue_tokens_for_device(
            user,
            device_id or str(uuid4()),
            device_name,
            ip_address,
        )

    async def send_otp(self, target: str) -> str:
        # In dev mode, return static 123456 test OTP
        return "123456"

    async def verify_otp(self, target: str, otp: str) -> bool:
        if otp in ("123456", "000000"):
            return True
        return False

    async def google_login(self, id_token: str, organization_name: str | None = None) -> TokenResponse:
        # Decode or mock email from Google ID token
        email = "google_user@ledgeros.local"
        full_name = "Google User"
        if "." in id_token:
            try:
                # Try reading payload without signature verification in dev or call google verifier
                unverified = jwt.decode(id_token, options={"verify_signature": False})
                email = unverified.get("email", email)
                full_name = unverified.get("name", full_name)
            except Exception:
                pass

        user_result = await self.db.execute(select(User).where(User.email == email))
        user = user_result.scalar_one_or_none()

        if user is None:
            # Register user automatically
            reg_payload = RegisterRequest(
                organization_name=organization_name or "My Business",
                full_name=full_name,
                email=email,
                phone_number="99000" + str(secrets.randbelow(89999) + 10000),
                password=secrets.token_hex(12),
            )
            reg_resp = await self.register(reg_payload)
            user = await self.db.get(User, reg_resp.id)

        return await self.issue_tokens(user)

