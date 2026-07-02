from app.config import Settings, get_settings


def test_settings_load_from_environment(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Custom Intake")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "true")

    settings = Settings()

    assert settings.app_name == "Custom Intake"
    assert settings.environment == "production"
    assert settings.debug is True


def test_get_settings_is_cached(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("APP_NAME", "Cached Intake")

    first = get_settings()
    second = get_settings()

    assert first is second
    assert first.app_name == "Cached Intake"

