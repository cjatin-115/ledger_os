import json
import urllib.error
import urllib.request

from app.core.config import settings

api_key = settings.GEMINI_API_KEY
print("API Key:", api_key[:10] if api_key else "None")

png_b64 = "iVBORw0KGgoAAAANSU5EUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYhxVSF4AAM20D/0y49A/AAAAAElFTkSuQmCC"

for model_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-1.5-flash"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": 'Analyze this image and return JSON: {"color": string, "status": "ok"}'
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": png_b64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.1,
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"SUCCESS with model {model_name}:", text)
            break
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        print(f"HTTPError {err.code} for {model_name}:\n{body}\n")
    except Exception as err:
        print(f"FAIL with model {model_name}:", err)
