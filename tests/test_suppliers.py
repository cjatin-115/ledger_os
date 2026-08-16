from uuid import UUID

import pytest
from httpx import AsyncClient

SUPPLIER_PAYLOAD = {
    "name": "ABC Electricals",
    "contact_person": "Rajesh Sharma",
    "phone": "9876543210",
    "email": "abc@example.com",
    "gstin": "27ABCDE1234F1Z5",
    "address": "Navi Mumbai",
    "payment_terms_days": 30,
}


@pytest.mark.asyncio
async def test_create_supplier(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/suppliers",
        json=SUPPLIER_PAYLOAD,
    )

    assert response.status_code == 201

    data = response.json()

    assert UUID(data["id"])
    assert data["name"] == "ABC Electricals"
    assert data["gstin"] == "27ABCDE1234F1Z5"
    assert data["payment_terms_days"] == 30
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_suppliers(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/suppliers",
        json=SUPPLIER_PAYLOAD,
    )

    assert create_response.status_code == 201

    response = await client.get("/api/v1/suppliers")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "ABC Electricals"


@pytest.mark.asyncio
async def test_get_supplier(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/suppliers",
        json=SUPPLIER_PAYLOAD,
    )

    assert create_response.status_code == 201

    supplier_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/suppliers/{supplier_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == supplier_id
    assert data["name"] == "ABC Electricals"


@pytest.mark.asyncio
async def test_get_nonexistent_supplier(
    client: AsyncClient,
) -> None:
    supplier_id = "00000000-0000-0000-0000-000000000099"

    response = await client.get(
        f"/api/v1/suppliers/{supplier_id}",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_supplier(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/suppliers",
        json=SUPPLIER_PAYLOAD,
    )

    assert create_response.status_code == 201

    supplier_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/suppliers/{supplier_id}",
        json={
            "payment_terms_days": 45,
            "phone": "9999999999",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["payment_terms_days"] == 45
    assert data["phone"] == "9999999999"
    assert data["name"] == "ABC Electricals"


@pytest.mark.asyncio
async def test_duplicate_gstin_is_rejected(
    client: AsyncClient,
) -> None:
    first_response = await client.post(
        "/api/v1/suppliers",
        json=SUPPLIER_PAYLOAD,
    )

    assert first_response.status_code == 201

    duplicate_payload = {
        **SUPPLIER_PAYLOAD,
        "name": "Another ABC",
    }

    second_response = await client.post(
        "/api/v1/suppliers",
        json=duplicate_payload,
    )

    assert second_response.status_code == 409
    assert "GSTIN" in second_response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_supplier_input(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/suppliers",
        json={
            "name": "",
            "payment_terms_days": -10,
        },
    )

    assert response.status_code == 422