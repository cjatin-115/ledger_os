import io
import json
import urllib.request
from PIL import Image

# 1. Login to get token
login_req = urllib.request.Request(
    'http://localhost:8000/api/v1/auth/login',
    data=json.dumps({'identifier': '9876543210', 'password': 'Demo@1234'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
login_res = json.loads(urllib.request.urlopen(login_req).read().decode('utf-8'))
token = login_res['access_token']
print("Got JWT Access Token!")

# 2. Upload image to /bills/scan-image
img = Image.new('RGB', (300, 300), color='white')
buf = io.BytesIO()
img.save(buf, format='JPEG')

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    'Content-Disposition: form-data; name="file"; filename="bill.jpg"\r\n'
    'Content-Type: image/jpeg\r\n\r\n'
).encode('utf-8') + buf.getvalue() + f'\r\n--{boundary}--\r\n'.encode('utf-8')

scan_req = urllib.request.Request(
    'http://localhost:8000/api/v1/bills/scan-image',
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': f'Bearer {token}',
    },
    method='POST',
)

with urllib.request.urlopen(scan_req) as resp:
    print("AI SCAN SUCCESS RESULT:", json.dumps(json.loads(resp.read().decode('utf-8')), indent=2))
