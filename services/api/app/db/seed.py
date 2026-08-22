from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PERMISSION_CATALOG
from app.db.models.bill import Bill, BillStatus
from app.db.models.organization import Organization
from app.db.models.organization_subscription import OrganizationSubscription
from app.db.models.permission import Permission
from app.db.models.role import Role
from app.db.models.role_permission import RolePermission
from app.db.models.subscription_plan import SubscriptionPlan
from app.db.models.supplier import Supplier
from app.db.models.user import User
from app.schemas.bill import BillCreate, BillItemCreate
from app.services.auth import AuthService
from app.services.bill import BillService

DEVELOPMENT_ORGANIZATION_ID = UUID("00000000-0000-0000-0000-000000000001")
DEVELOPMENT_USER_ID = UUID("00000000-0000-0000-0000-000000000002")
DEVELOPMENT_ROLE_ID = UUID("00000000-0000-0000-0000-000000000003")
DEVELOPMENT_SUPPLIER_ID = UUID("00000000-0000-0000-0000-000000000004")
DEVELOPMENT_PLAN_ID = UUID("00000000-0000-0000-0000-000000000005")

DEMO_PASSWORD = "Demo@1234"
DEMO_PHONE = "9876543210"
DEMO_EMAIL = "demo@ledgeros.local"


async def seed_development_data(db: AsyncSession) -> None:
    """Create deterministic local development records with a login-ready demo account."""

    permission_result = await db.execute(
        select(Permission).where(Permission.code.in_(PERMISSION_CATALOG.keys()))
    )
    permissions = {p.code: p for p in permission_result.scalars().all()}
    for code, (description, category) in PERMISSION_CATALOG.items():
        if code not in permissions:
            permission = Permission(code=code, description=description, category=category)
            db.add(permission)
            await db.flush()
            permissions[code] = permission

    organization = await db.get(Organization, DEVELOPMENT_ORGANIZATION_ID)
    if organization is None:
        organization = Organization(
            id=DEVELOPMENT_ORGANIZATION_ID,
            name="LedgerOS Demo Shop",
            gstin="27DEMOSHOP001Z5",
            email=DEMO_EMAIL,
            phone=DEMO_PHONE,
            is_active=True,
        )
        db.add(organization)
    else:
        organization.name = "LedgerOS Demo Shop"
        organization.email = DEMO_EMAIL
        organization.phone = DEMO_PHONE

    trial_plan = await db.scalar(
        select(SubscriptionPlan).where(SubscriptionPlan.code == "free_trial")
    )
    if trial_plan is None:
        trial_plan = SubscriptionPlan(
            id=DEVELOPMENT_PLAN_ID,
            code="free_trial",
            name="Free Trial",
            max_devices=5,
            price_per_device=0,
            currency="INR",
            billing_interval="monthly",
            trial_days=365,
            is_active=True,
        )
        db.add(trial_plan)
        await db.flush()

    existing_sub = await db.scalar(
        select(OrganizationSubscription).where(
            OrganizationSubscription.organization_id == DEVELOPMENT_ORGANIZATION_ID
        )
    )
    if existing_sub is None:
        now = datetime.now(UTC)
        db.add(
            OrganizationSubscription(
                organization_id=DEVELOPMENT_ORGANIZATION_ID,
                plan_id=trial_plan.id,
                status="active",
                starts_at=now,
                ends_at=now + timedelta(days=365),
            )
        )

    role = await db.get(Role, DEVELOPMENT_ROLE_ID)
    if role is None:
        role = Role(
            id=DEVELOPMENT_ROLE_ID,
            organization_id=DEVELOPMENT_ORGANIZATION_ID,
            name="OWNER",
            description="Development owner role",
            is_active=True,
        )
        db.add(role)

    for permission in permissions.values():
        existing_link = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == DEVELOPMENT_ROLE_ID,
                RolePermission.permission_id == permission.id,
            )
        )
        if existing_link.scalar_one_or_none() is None:
            db.add(
                RolePermission(role_id=DEVELOPMENT_ROLE_ID, permission_id=permission.id)
            )

    user = await db.get(User, DEVELOPMENT_USER_ID)
    password_hash = AuthService.hash_password(DEMO_PASSWORD)
    if user is None:
        user = User(
            id=DEVELOPMENT_USER_ID,
            organization_id=DEVELOPMENT_ORGANIZATION_ID,
            role_id=DEVELOPMENT_ROLE_ID,
            phone_number=DEMO_PHONE,
            full_name="Demo Shop Owner",
            email=DEMO_EMAIL,
            password_hash=password_hash,
            is_active=True,
        )
        db.add(user)
    else:
        user.phone_number = DEMO_PHONE
        user.email = DEMO_EMAIL
        user.full_name = "Demo Shop Owner"
        user.password_hash = password_hash
        user.is_active = True

    supplier = await db.get(Supplier, DEVELOPMENT_SUPPLIER_ID)
    if supplier is None:
        supplier = Supplier(
            id=DEVELOPMENT_SUPPLIER_ID,
            organization_id=DEVELOPMENT_ORGANIZATION_ID,
            name="Metro Electricals",
            contact_person="Ravi Kumar",
            phone="9988776655",
            email="accounts@metroe.in",
            gstin="27METROELEC01Z5",
            address="12 Industrial Area, Pune",
            payment_terms_days=30,
            is_active=True,
        )
        db.add(supplier)

    await db.commit()

    existing_bill = await db.scalar(
        select(Bill).where(
            Bill.organization_id == DEVELOPMENT_ORGANIZATION_ID,
            Bill.bill_number == "INV-2048",
        )
    )
    if existing_bill is None:
        bill_service = BillService(db)
        bill = await bill_service.create(
            BillCreate(
                supplier_id=DEVELOPMENT_SUPPLIER_ID,
                bill_number="INV-2048",
                bill_date=datetime.now(UTC).date() - timedelta(days=10),
                due_date=datetime.now(UTC).date() + timedelta(days=2),
                subtotal=Decimal("27542.37"),
                discount_amount=Decimal("0.00"),
                taxable_amount=Decimal("27542.37"),
                cgst_amount=Decimal("2478.81"),
                sgst_amount=Decimal("2478.81"),
                igst_amount=Decimal("0.00"),
                total_amount=Decimal("32500.00"),
                notes="Demo bill for testing payment allocation",
                items=[
                    BillItemCreate(
                        description="LED Panel 18W",
                        quantity=Decimal("20"),
                        unit="PCS",
                        unit_price=Decimal("500.00"),
                        discount_amount=Decimal("0.00"),
                        tax_rate=Decimal("18.00"),
                        tax_amount=Decimal("1800.00"),
                        line_total=Decimal("11800.00"),
                    ),
                    BillItemCreate(
                        description="Copper Wire 2.5mm",
                        quantity=Decimal("50"),
                        unit="MTR",
                        unit_price=Decimal("314.85"),
                        discount_amount=Decimal("0.00"),
                        tax_rate=Decimal("18.00"),
                        tax_amount=Decimal("2833.65"),
                        line_total=Decimal("18576.15"),
                    ),
                ],
            ),
            organization_id=DEVELOPMENT_ORGANIZATION_ID,
        )
        await bill_service.post(bill.id, DEVELOPMENT_ORGANIZATION_ID)

    print("\n=== LedgerOS Demo Account ===")
    print(f"Phone:    {DEMO_PHONE}")
    print(f"Email:    {DEMO_EMAIL}")
    print(f"Password: {DEMO_PASSWORD}")
    print("Shop:     LedgerOS Demo Shop")
    print("Supplier: Metro Electricals (open bill INV-2048 for Rs.32,500)")
    print("=============================\n")
