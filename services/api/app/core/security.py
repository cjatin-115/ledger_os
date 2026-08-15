def get_security_headers() -> dict[str, str]:
    return {"X-Content-Type-Options": "nosniff"}
