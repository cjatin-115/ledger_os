from uuid import UUID

import pytest
from httpx import AsyncClient

SUPPLIER_ID = "00000000-0000-0000-0000-000000000011"

BILL_PAYLOAD = {
    "supplier_id": SUPPLIER_ID,
    "bill_number": "TEST-INV-1001",
    "bill_date": "2026-08-16",
    "due_date": "2026-09-15",
    "subtotal": 10000.00,
    "discount_amount": 500.00,
    "taxable_amount": 9500.00,
    "cgst_amount": 855.00,
    "sgst_amount": 855.00,
    "igst_amount": 0.00,
    "total_amount": 11210.00,
    "notes": "Test bill",
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


@pytest.mark.asyncio
async def test_create_bill(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert response.status_code == 201

    data = response.json()

    assert UUID(data["id"])
    assert data["bill_number"] == "TEST-INV-1001"
    assert data["status"] == "draft"
    assert data["source_type"] == "manual"
    assert len(data["items"]) == 2
    assert data["items"][0]["description"] == "LED Panel 18W"


@pytest.mark.asyncio
async def test_list_bills(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert response.status_code == 201

    response = await client.get("/api/v1/bills")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["bill_number"] == "TEST-INV-1001"
    assert len(data[0]["items"]) == 2


@pytest.mark.asyncio
async def test_get_bill(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert create_response.status_code == 201

    bill_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/bills/{bill_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == bill_id
    assert data["bill_number"] == "TEST-INV-1001"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_duplicate_bill_number_is_rejected(
    client: AsyncClient,
) -> None:
    first_response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_bill_cannot_have_due_date_before_bill_date(
    client: AsyncClient,
) -> None:
    payload = {
        **BILL_PAYLOAD,
        "bill_number": "TEST-INV-1002",
        "bill_date": "2026-08-16",
        "due_date": "2026-08-01",
    }

    response = await client.post(
        "/api/v1/bills",
        json=payload,
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_bill_requires_existing_supplier(
    client: AsyncClient,
) -> None:
    payload = {
        **BILL_PAYLOAD,
        "bill_number": "TEST-INV-1003",
        "supplier_id": "00000000-0000-0000-0000-000000000099",
    }

    response = await client.post(
        "/api/v1/bills",
        json=payload,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_bill_input(
    client: AsyncClient,
) -> None:
    payload = {
        **BILL_PAYLOAD,
        "bill_number": "",
        "subtotal": -100,
    }

    response = await client.post(
        "/api/v1/bills",
        json=payload,
    )

    assert response.status_code == 422