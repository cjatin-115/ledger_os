import google.generativeai as genai
from PIL import Image

from app.core.config import settings

api_key = settings.GEMINI_API_KEY
print("Key:", api_key)

genai.configure(api_key=api_key)

img = Image.new("RGB", (100, 100), color="white")

for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(['Return JSON: {"status": "ok"}', img])
        print(f"SUCCESS WITH {model_name}:", response.text)
        break
    except Exception as e:
        print(f"FAIL WITH {model_name}:", e)
