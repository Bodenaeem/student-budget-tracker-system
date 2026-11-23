"""Runtime settings for local development and single-owner hosted use."""

import hmac
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    database_path: Path
    demo_login: bool
    ephemeral_storage: bool = False

    def authenticate(self, username: str, password: str) -> bool:
        username_matches = hmac.compare_digest(username.encode(), self.username.encode())
        password_matches = hmac.compare_digest(password.encode(), self.password.encode())
        return username_matches and password_matches


def load_settings(app_directory: Path, environ=None) -> Settings:
    env = os.environ if environ is None else environ
    mode = env.get("BUDGET_DEPLOYMENT", "local")
    if mode not in {"local", "production"}:
        raise ValueError("BUDGET_DEPLOYMENT must be local or production.")
    on_vercel = env.get("VERCEL") == "1"
    hosted = mode == "production" or env.get("RENDER") == "true" or bool(env.get("RAILWAY_PROJECT_ID")) or on_vercel
    username = env.get("BUDGET_USERNAME", "")
    password = env.get("BUDGET_PASSWORD", "")
    if hosted and (not username.strip() or len(password) < 12 or password == "admin123"):
        raise ValueError("Set BUDGET_USERNAME and a private BUDGET_PASSWORD of at least 12 characters in the host's secret settings.")
    if bool(username) != bool(password):
        raise ValueError("Set both BUDGET_USERNAME and BUDGET_PASSWORD.")
    database = env.get("BUDGET_DB_PATH", "")
    if hosted and (not database or not Path(database).is_absolute()):
        raise ValueError("Set BUDGET_DB_PATH to an absolute file path on the host's persistent disk.")
    return Settings(
        username=username or "admin",
        password=password or "admin123",
        database_path=Path(database) if database else app_directory / "smart_budget_tracker.db",
        demo_login=not username and not hosted,
        ephemeral_storage=on_vercel or env.get("BUDGET_STORAGE") == "ephemeral",
    )
