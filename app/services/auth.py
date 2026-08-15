class AuthService:
    def login(self) -> dict[str, str]:
        return {"access_token": "demo-token", "token_type": "bearer"}
