import json
import uuid
import urllib.request

# 1. Register fresh user
email = f"user-{uuid.uuid4().hex[:6]}@test.com"
phone = f"99{uuid.uuid4().int % 10**8:08d}"

reg_req = urllib.request.Request(
    'http://localhost:8000/api/v1/auth/register',
    data=json.dumps({
        'organization_name': 'Mayur Shop',
        'full_name': 'Owner',
        'email': email,
        'phone_number': phone,
        'password': 'StrongPass!123',
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
reg_res = json.loads(urllib.request.urlopen(reg_req).read().decode('utf-8'))

# 2. Login
login_req = urllib.request.Request(
    'http://localhost:8000/api/v1/auth/login',
    data=json.dumps({'identifier': email, 'password': 'StrongPass!123'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
login_res = json.loads(urllib.request.urlopen(login_req).read().decode('utf-8'))
token = login_res['access_token']

# 3. Confirm scan payload (Mayur Trading Co)
payload = {
    "supplier_name": "MAYUR TRADING CO",
    "supplier_gstin": "27CQEPC9373C1ZW",
    "bill_number": "MTC/019/2026-27",
    "bill_date": "2026-08-19",
    "subtotal": "11440.50",
    "discount_amount": "0.00",
    "taxable_amount": "11440.50",
    "cgst_amount": "1029.65",
    "sgst_amount": "1029.65",
    "igst_amount": "0.00",
    "total_amount": "13500.00",
    "items": [
        {
            "description": "O 20W GRACE PRO LED BATTEN 6500K",
            "quantity": "150.0",
            "unit": "NOS",
            "unit_price": "76.27",
            "discount_amount": "0.00",
            "tax_rate": "18.00",
            "tax_amount": "2059.30",
            "line_total": "11440.50"
        }
    ],
    "confidence": "0.95",
    "warnings": []
}

confirm_req = urllib.request.Request(
    'http://localhost:8000/api/v1/bills/scan/confirm',
    data=json.dumps(payload).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    },
    method='POST',
)

try:
    with urllib.request.urlopen(confirm_req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print("[OK] CONFIRM SCAN SUCCESS!")
        print("Supplier Match:", result['supplier_match'])
        print("Saved Bill ID:", result['bill']['id'])
        print("Bill Total Amount:", result['bill']['total_amount'])
        print("Bill Status:", result['bill']['status'])
except urllib.error.HTTPError as err:
    print("HTTP ERROR:", err.code, err.read().decode('utf-8'))
