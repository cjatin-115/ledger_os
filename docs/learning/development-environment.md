uv is currently blocked by Windows Application Control policy.

Temporary workaround:
activate .venv

python -m pytest
python -m ruff check .

Do not disable Windows security policies just to run uv.
Investigate the policy later.