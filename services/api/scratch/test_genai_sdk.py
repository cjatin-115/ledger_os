import io

from google import genai
from google.genai import types
from PIL import Image

from app.core.config import settings

api_key = settings.GEMINI_API_KEY
client = genai.Client(api_key=api_key)

img = Image.new("RGB", (100, 100), color="white")
img_bytes = io.BytesIO()
img.save(img_bytes, format="JPEG")

for model in [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.6-flash",
]:
    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                'Return JSON: {"status": "ok"}',
                types.Part.from_bytes(
                    data=img_bytes.getvalue(), mime_type="image/jpeg"
                ),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        print(f"SUCCESS WITH MODEL {model}:", response.text)
        break
    except Exception as e:
        print(f"FAIL WITH MODEL {model}:", e)
