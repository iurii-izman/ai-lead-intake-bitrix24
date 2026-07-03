from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.services.admin_dashboard import AdminDashboardService, _mask_free_text


def test_gitignore_contains_security_entries() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    for entry in [
        ".env",
        ".env.*",
        "!.env.example",
        "*.sqlite",
        "*.db",
        "data/",
        "logs/",
        "__pycache__/",
        ".pytest_cache/",
    ]:
        assert entry in gitignore


def test_admin_settings_snapshot_masks_secrets() -> None:
    service = AdminDashboardService(
        settings=Settings(
            database_url="sqlite+pysqlite:///./local.sqlite3",
            intake_webhook_secret="super-secret-token",
            admin_username="admin",
            admin_password="another-secret",
            openai_api_key="sk-test-123",
        )
    )

    snapshot = service.get_settings_snapshot()
    runtime = dict(snapshot.runtime)

    assert runtime["database_url"] == "sqlite+pysqlite:///./local.sqlite3"
    assert runtime["intake_webhook_secret"] == "[masked]"
    assert runtime["admin_password"] == "[masked]"
    assert runtime["openai_api_key"] == "[masked]"


def test_free_text_masking_redacts_email_and_phone() -> None:
    masked = _mask_free_text(
        "Call Ivan Petrov at ivan.petrov@example.com or +37360000000 for details."
    )

    assert "ivan.petrov@example.com" not in masked
    assert "+37360000000" not in masked
    assert "[masked email]" in masked
    assert "[masked phone]" in masked
