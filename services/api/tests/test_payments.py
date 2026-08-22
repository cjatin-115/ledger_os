from decimal import Decimal
from uuid import UUID

import pytest
from httpx import AsyncClient

SUPPLIER_ID = "00000000-0000-0000-0000-000000000011"


BILL_PAYLOAD = {
    "supplier_id": SUPPLIER_ID,
    "bill_number": "TEST-PAY-1001",
    "bill_date": "2026-08-16",
    "due_date": "2026-09-15",
    "subtotal": 10000.00,
    "discount_amount": 500.00,
    "taxable_amount": 9500.00,
    "cgst_amount": 855.00,
    "sgst_amount": 855.00,
    "igst_amount": 0.00,
    "total_amount": 11210.00,
    "notes": "Payment test bill",
    "items": [
        {
            "description": "LED Panel 18W",
            "quantity": 10,
            "unit": "PCS",
            "unit_price": 500.00,
            "discount_amount": 0.00,
            "tax_rate": 18.00,
            "tax_amount": 900.00,
            "line_total": 5900.00,
            "hsn_code": "9405",
        },
        {
            "description": "PVC Casing 20mm",
            "quantity": 20,
            "unit": "PCS",
            "unit_price": 200.00,
            "discount_amount": 0.00,
            "tax_rate": 18.00,
            "tax_amount": 720.00,
            "line_total": 4720.00,
            "hsn_code": "3917",
        },
    ],
}


PAYMENT_PAYLOAD = {
    "supplier_id": SUPPLIER_ID,
    "amount": 5000.00,
    "payment_method": "upi",
    "payment_date": "2026-08-16",
    "reference_number": "UPI-TEST-001",
    "notes": "Payment test",
}


@pytest.mark.asyncio
async def test_create_payment(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/payments",
        json=PAYMENT_PAYLOAD,
    )

    assert response.status_code == 201

    data = response.json()

    assert UUID(data["id"])
    assert data["supplier_id"] == SUPPLIER_ID
    assert Decimal(data["amount"]) == Decimal("5000.00")
    assert data["payment_method"] == "upi"
    assert data["status"] == "recorded"


@pytest.mark.asyncio
async def test_get_payment(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/payments",
        json={
            **PAYMENT_PAYLOAD,
            "reference_number": "UPI-TEST-002",
        },
    )

    assert create_response.status_code == 201

    payment_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/payments/{payment_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == payment_id


@pytest.mark.asyncio
async def test_list_payments(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/payments",
        json={
            **PAYMENT_PAYLOAD,
            "reference_number": "UPI-TEST-003",
        },
    )

    assert create_response.status_code == 201

    response = await client.get("/api/v1/payments")

    assert response.status_code == 200

    data = response.json()

    assert any(
        payment["id"] == create_response.json()["id"]
        for payment in data
    )


@pytest.mark.asyncio
async def test_payment_requires_existing_supplier(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/payments",
        json={
            **PAYMENT_PAYLOAD,
            "supplier_id": "00000000-0000-0000-0000-000000000099",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_payment_method(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/payments",
        json={
            **PAYMENT_PAYLOAD,
            "payment_method": "bitcoin",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_full_payment_allocation(
    client: AsyncClient,
) -> None:
    bill_response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert bill_response.status_code == 201

    bill_id = bill_response.json()["id"]

    post_response = await client.post(
        f"/api/v1/bills/{bill_id}/post",
    )

    assert post_response.status_code == 200
    assert post_response.json()["status"] == "posted"

    payment_response = await client.post(
        "/api/v1/payments",
        json=PAYMENT_PAYLOAD,
    )

    assert payment_response.status_code == 201

    payment_id = payment_response.json()["id"]

    allocation_response = await client.post(
        f"/api/v1/payments/{payment_id}/allocate",
        json={
            "bill_id": bill_id,
            "amount": 5000.00,
        },
    )

    assert allocation_response.status_code == 200

    allocation = allocation_response.json()

    assert allocation["payment_id"] == payment_id
    assert allocation["bill_id"] == bill_id
    assert Decimal(allocation["amount"]) == Decimal("5000.00")

    