from __future__ import annotations

import io
import json
import logging
import re
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None

from app.core.config import settings

logger = logging.getLogger(__name__)


def _clean_json_string(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def call_gemini_vision(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    preferred_model: str = "gemini-3.6-flash",
) -> dict[str, Any] | None:
    """Call Google Gemini Vision API using Google GenAI SDK to analyze image content and return structured JSON."""
    api_key = settings.GEMINI_API_KEY
    if not api_key or genai is None:
        logger.info("GEMINI_API_KEY is not set or google-genai is missing. Using local fallback.")
        print("[Gemini AI] GEMINI_API_KEY is empty. Using local OCR fallback.")
        return None

    # Handle auto-rotation of paper bill photos (EXIF orientation)
    processed_bytes = image_bytes
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        out_io = io.BytesIO()
        pil_img.save(out_io, format="JPEG", quality=90)
        processed_bytes = out_io.getvalue()
        mime_type = "image/jpeg"
    except Exception as img_err:
        logger.warning(f"Image preprocessing warning: {img_err}")

    models_to_try = [
        preferred_model,
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-3.1-pro-preview",
    ]

    try:
        client = genai.Client(api_key=api_key)
    except Exception as exc:
        print(f"[Gemini AI Error] Could not initialize GenAI Client: {exc}")
        return None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=processed_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            text_content = response.text
            if not text_content:
                continue

            cleaned_text = _clean_json_string(text_content)
            parsed_json = json.loads(cleaned_text)
            print(f"[Gemini AI] Successfully extracted invoice using model: {model_name}")
            return parsed_json
        except Exception as exc:
            print(f"[Gemini AI Warning] Model {model_name} failed: {exc}. Trying next model...")
            logger.warning(f"Gemini API vision call failed on {model_name}: {exc}")

    return None
