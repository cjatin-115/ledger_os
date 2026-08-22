
import pytest
from httpx import AsyncClient

from app.db.models.supplier import Supplier
from app.db.session import AsyncSessionLocal

SUPPLIER_ID = "00000000-0000-0000-0000-000000000011"

BILL_PAYLOAD = {
    "supplier_id": SUPPLIER_ID,
    "bill_number": "TEST-CREATE-1001",
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
async def test_scan_bill_extracts_invoice_data(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/bills/scan",
        json={
            "raw_text": """ABC HARDWARE\nGSTIN: 27XXXXXXXXXXXXX\nInvoice No: INV-1045\nDate: 20/08/2026\n1 PVC Pipe 10 PCS 120.00 1200\n2 Elbow 20 PCS 25.00 500\nSubtotal: 1700\nCGST: 153\nSGST: 153\nTOTAL: 2006\n""",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["supplier_name"] == "ABC HARDWARE"
    assert data["supplier_gstin"] == "27XXXXXXXXXXXXX"
    assert data["bill_number"] == "INV-1045"
    assert data["bill_date"] == "2026-08-20"
    assert data["subtotal"] == "1700.00"
    assert data["total_amount"] == "2006.00"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_confirm_scan_creates_draft_bill(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/bills/scan/confirm",
        json={
            "supplier_name": "ABC HARDWARE",
            "supplier_gstin": "27ABCDE1234F1Z5",
            "bill_number": "INV-2048",
            "bill_date": "2026-08-20",
            "subtotal": "1700.00",
            "discount_amount": "0.00",
            "taxable_amount": "1700.00",
            "cgst_amount": "153.00",
            "sgst_amount": "153.00",
            "igst_amount": "0.00",
            "total_amount": "2006.00",
            "items": [
                {
                    "description": "PVC Pipe",
                    "quantity": "10",
                    "unit": "PCS",
                    "unit_price": "120.00",
                    "discount_amount": "0.00",
                    "tax_rate": "18.00",
                    "tax_amount": "216.00",
                    "line_total": "1200.00",
                },
                {
                    "description": "Elbow",
                    "quantity": "20",
                    "unit": "PCS",
                    "unit_price": "25.00",
                    "discount_amount": "0.00",
                    "tax_rate": "18.00",
                    "tax_amount": "90.00",
                    "line_total": "500.00",
                },
            ],
            "confidence": "0.93",
            "warnings": [],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["supplier_match"]["found"] is True
    assert data["bill"]["bill_number"] == "INV-2048"
    assert data["bill"]["status"] == "draft"


@pytest.mark.asyncio
async def test_create_bill(client: AsyncClient) -> None:
    async with AsyncSessionLocal() as db:
        supplier = await db.get(
            Supplier,
            "00000000-0000-0000-0000-000000000011",
        )

        assert supplier is not None

    await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )


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
    assert data[0]["bill_number"] == "TEST-CREATE-1001"
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
    assert data["bill_number"] == "TEST-CREATE-1001"
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
        "bill_number": "TEST-CREATE-1002",
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
        "bill_number": "TEST-CREATE-1003",
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

@pytest.mark.asyncio
async def test_post_bill_creates_ledger_transaction(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/bills",
        json=BILL_PAYLOAD,
    )

    assert create_response.status_code == 201

    bill_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/bills/{bill_id}/post",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == bill_id
    assert data["status"] == "posted"


@pytest.mark.asyncio
async def test_posting_bill_twice_is_rejected(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/bills",
        json={
            **BILL_PAYLOAD,
            "bill_number": "TEST-POST-1001",
        },
    )

    assert create_response.status_code == 201

    bill_id = create_response.json()["id"]

    first_post = await client.post(
        f"/api/v1/bills/{bill_id}/post",
    )

    assert first_post.status_code == 200

    second_post = await client.post(
        f"/api/v1/bills/{bill_id}/post",
    )

    assert second_post.status_code == 409


@pytest.mark.asyncio
async def test_scan_bill_image_extracts_data(
    client: AsyncClient,
) -> None:
    files = {"file": ("test_bill.jpg", b"fake_image_bytes_content", "image/jpeg")}
    response = await client.post(
        "/api/v1/bills/scan-image",
        files=files,
    )

    assert response.status_code == 200
    data = response.json()
    assert "supplier_name" in data
    assert "total_amount" in data