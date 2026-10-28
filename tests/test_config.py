import re
from pathlib import Path

from intel.config import CONFIG_KEYS, DEFAULT_DB_PATH, load_settings

ROOT = Path(__file__).resolve().parents[1]


def test_every_config_key_is_in_env_example():
    example = (ROOT / ".env.example").read_text()
    declared = set(re.findall(r"^([A-Z_]+)=", example, re.M))
    assert set(CONFIG_KEYS) <= declared


def test_environment_is_read_only_through_config_module():
    offenders = [
        p.name
        for p in (ROOT / "src" / "intel").rglob("*.py")
        if p.name != "config.py" and re.search(r"os\.environ|getenv\(", p.read_text())
    ]
    assert offenders == []


def test_defaults_apply_when_unset(monkeypatch):
    for key in CONFIG_KEYS:
        monkeypatch.setenv(key, "")
    settings = load_settings()
    assert settings.db_path == Path(DEFAULT_DB_PATH)
    assert settings.llm_api_key is None
