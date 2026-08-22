from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.rate_limit import rate_limit
from app.db.models.coupon import Coupon, CouponRedemption
from app.db.models.organization_subscription import OrganizationSubscription
from app.db.models.subscription_plan import SubscriptionPlan
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import (
    DeviceSessionResponse,
    GoogleAuthRequest,
    LoginRequest,
    MFAConfirmRequest,
    MFASetupResponse,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    SendOTPRequest,
    SendOTPResponse,
    TokenResponse,
    UserProfileResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(db)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
    _: None = Depends(rate_limit("auth-register", 5, 60)),
) -> RegisterResponse:
    try:
        return await service.register(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
    _: None = Depends(rate_limit("auth-login", 10, 60)),
) -> TokenResponse:
    try:
        return await service.login(
            payload.login_identifier(),
            payload.password,
            payload.otp,
            payload.device_id,
            payload.device_name,
            request.client.host if request.client else None,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await service.refresh(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/otp/send", response_model=SendOTPResponse)
async def send_otp(
    payload: SendOTPRequest,
    service: AuthService = Depends(get_auth_service),
) -> SendOTPResponse:
    target = payload.phone_number or payload.email or ""
    if not target:
        raise HTTPException(status_code=400, detail="Phone number or email is required.")
    otp = await service.send_otp(target)
    return SendOTPResponse(
        message=f"Verification OTP sent to {target}.",
        test_otp=otp,
    )


@router.post("/otp/verify", response_model=VerifyOTPResponse)
async def verify_otp(
    payload: VerifyOTPRequest,
    service: AuthService = Depends(get_auth_service),
) -> VerifyOTPResponse:
    target = payload.phone_number or payload.email or ""
    verified = await service.verify_otp(target, payload.otp)
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    return VerifyOTPResponse(verified=True, message="OTP verified successfully.")


@router.post("/google", response_model=TokenResponse)
async def google_login(
    payload: GoogleAuthRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    try:
        return await service.google_login(payload.id_token, payload.organization_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/password-reset/request",
    response_model=PasswordResetResponse,
)
async def request_password_reset(
    payload: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
    _: None = Depends(rate_limit("auth-password-reset", 3, 300)),
) -> PasswordResetResponse:
    return await service.request_password_reset(payload)


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetResponse,
)
async def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    service: AuthService = Depends(get_auth_service),
) -> PasswordResetResponse:
    try:
        return await service.confirm_password_reset(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=UserProfileResponse)
async def me(
    user: User = Depends(require_permission("auth.me")),
) -> UserProfileResponse:
    return UserProfileResponse(
        id=user.id,
        organization_id=user.organization_id,
        role_id=user.role_id,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        is_active=user.is_active,
    )


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    user: User = Depends(require_permission("auth.me")),
    service: AuthService = Depends(get_auth_service),
) -> MFASetupResponse:
    return await service.setup_mfa(user)


@router.post("/mfa/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_mfa(
    payload: MFAConfirmRequest,
    user: User = Depends(require_permission("auth.me")),
    service: AuthService = Depends(get_auth_service),
) -> None:
    try:
        await service.confirm_mfa(user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/mfa", status_code=status.HTTP_204_NO_CONTENT)
async def disable_mfa(
    user: User = Depends(require_permission("auth.me")),
    service: AuthService = Depends(get_auth_service),
) -> None:
    await service.disable_mfa(user)


@router.get("/devices", response_model=list[DeviceSessionResponse])
async def list_devices(
    user: User = Depends(require_permission("auth.me")),
    service: AuthService = Depends(get_auth_service),
) -> list[DeviceSessionResponse]:
    return await service.list_device_sessions(user)


@router.delete("/devices/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_device(
    session_id: UUID,
    user: User = Depends(require_permission("auth.me")),
    service: AuthService = Depends(get_auth_service),
) -> None:
    try:
        await service.revoke_device_session(user, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/redeem-coupon")
async def redeem_coupon(
    code: str,
    user: User = Depends(require_permission("auth.me")),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    coupon = await db.scalar(select(Coupon).where(Coupon.code == code.strip().upper()).with_for_update())
    if (
        coupon is None
        or not coupon.is_active
        or (coupon.max_redemptions is not None and coupon.redemption_count >= coupon.max_redemptions)
    ):
        raise HTTPException(status_code=400, detail="Coupon is invalid or exhausted.")
    plan = await db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == coupon.plan_code))
    if plan is None:
        raise HTTPException(status_code=400, detail="Coupon plan is unavailable.")
    existing = await db.scalar(
        select(CouponRedemption).where(
            CouponRedemption.coupon_id == coupon.id,
            CouponRedemption.organization_id == user.organization_id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Coupon already redeemed.")
    subscription = await db.scalar(
        select(OrganizationSubscription).where(OrganizationSubscription.organization_id == user.organization_id)
    )
    if subscription is None:
        raise HTTPException(
            status_code=400,
            detail="Organization subscription is unavailable.",
        )
    subscription.plan_id = plan.id
    subscription.status = "active"
    coupon.redemption_count += 1
    db.add(
        CouponRedemption(
            coupon_id=coupon.id,
            organization_id=user.organization_id,
            redeemed_by=user.id,
        )
    )
    await db.commit()
    return {"status": "redeemed", "plan": plan.code}
