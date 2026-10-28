"""Settings loaded from environment variables (and a local .env, if present).

Every key read here must also appear in .env.example; tests enforce this.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

CONFIG_KEYS = (
    "INTEL_DB_PATH",
    "INTEL_WEB_DIST",
    "SEC_USER_AGENT",
    "LLM_BASE_URL",
    "LLM_MODEL",
    "LLM_API_KEY",
    "LLM_VERIFY_BASE_URL",
    "LLM_VERIFY_MODEL",
    "LLM_VERIFY_API_KEY",
)

DEFAULT_DB_PATH = "data/processed/intel.db"
DEFAULT_WEB_DIST = "web/dist"


@dataclass(frozen=True)
class Settings:
    db_path: Path
    web_dist: Path
    sec_user_agent: str | None
    llm_base_url: str | None
    llm_model: str | None
    llm_api_key: str | None
    llm_verify_base_url: str | None
    llm_verify_model: str | None
    llm_verify_api_key: str | None


def load_settings() -> Settings:
    load_dotenv()
    env = {key: os.environ.get(key) or None for key in CONFIG_KEYS}
    return Settings(
        db_path=Path(env["INTEL_DB_PATH"] or DEFAULT_DB_PATH),
        web_dist=Path(env["INTEL_WEB_DIST"] or DEFAULT_WEB_DIST),
        sec_user_agent=env["SEC_USER_AGENT"],
        llm_base_url=env["LLM_BASE_URL"],
        llm_model=env["LLM_MODEL"],
        llm_api_key=env["LLM_API_KEY"],
        llm_verify_base_url=env["LLM_VERIFY_BASE_URL"],
        llm_verify_model=env["LLM_VERIFY_MODEL"],
        llm_verify_api_key=env["LLM_VERIFY_API_KEY"],
    )
