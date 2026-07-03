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


def test_rate_limit_settings_load_from_environment(monkeypatch):
    monkeypatch.setenv("INTAKE_RATE_LIMIT_MAX_REQUESTS", "7")
    monkeypatch.setenv("INTAKE_RATE_LIMIT_WINDOW_SECONDS", "15")

    settings = Settings()

    assert settings.intake_rate_limit_max_requests == 7
    assert settings.intake_rate_limit_window_seconds == 15


def test_legacy_rate_limit_setting_is_supported(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_INTAKE", "10/minute")

    settings = Settings()

    assert settings.intake_rate_limit_max_requests == 10
    assert settings.intake_rate_limit_window_seconds == 60
