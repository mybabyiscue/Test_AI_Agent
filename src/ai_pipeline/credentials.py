from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import project_root


class CredentialNotFoundError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PlatformCredential:
    platform: str
    token: str
    profile: str
    source: str

    def redacted(self) -> dict[str, str]:
        return {
            "platform": self.platform,
            "profile": self.profile,
            "token": _redact_token(self.token),
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class DatabaseCredential:
    profile: str
    type: str
    host: str
    port: int
    user: str
    password: str
    source: str
    description: str = ""

    def redacted(self) -> dict[str, object]:
        return {
            "profile": self.profile,
            "type": self.type,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": _redact_token(self.password),
            "source": self.source,
            "description": self.description,
        }


class EnvCredentialProvider:
    def __init__(
        self,
        credentials_file: Path | None = project_root() / "config" / "credentials.local.json",
    ) -> None:
        self.credentials_file = credentials_file

    def get(self, platform: str, profile: str = "default") -> PlatformCredential:
        normalized_platform = _normalize_name(platform)
        normalized_profile = _normalize_name(profile)

        file_credential = self._get_from_file(normalized_platform, normalized_profile)
        if file_credential is not None:
            return file_credential

        env_name = _build_token_env_name(normalized_platform, normalized_profile)
        token = os.getenv(env_name)
        if not token:
            raise CredentialNotFoundError(
                f"未找到平台凭证：platform={platform}, profile={profile}, env={env_name}, file={self.credentials_file}"
            )

        return PlatformCredential(
            platform=normalized_platform.lower(),
            token=token,
            profile=normalized_profile.lower(),
            source=f"env:{env_name}",
        )

    def get_database(self, profile: str) -> DatabaseCredential:
        normalized_profile = _normalize_name(profile).lower()

        file_credential = self._get_database_from_file(normalized_profile)
        if file_credential is not None:
            return file_credential

        prefix = normalized_profile.upper()
        host = os.getenv(f"{prefix}_DB_HOST")
        port = os.getenv(f"{prefix}_DB_PORT")
        user = os.getenv(f"{prefix}_DB_USER")
        password = os.getenv(f"{prefix}_DB_PASSWORD")
        if not all([host, port, user, password]):
            raise CredentialNotFoundError(
                f"未找到数据库凭证：profile={profile}, env_prefix={prefix}_DB_*, file={self.credentials_file}"
            )

        return DatabaseCredential(
            profile=normalized_profile,
            type="mysql",
            host=str(host),
            port=int(str(port)),
            user=str(user),
            password=str(password),
            source=f"env:{prefix}_DB_*",
        )

    def _get_from_file(self, platform: str, profile: str) -> PlatformCredential | None:
        if self.credentials_file is None or not self.credentials_file.exists():
            return None

        payload = json.loads(self.credentials_file.read_text(encoding="utf-8-sig"))
        platforms: dict[str, Any] = payload.get("platforms", {})
        platform_config = platforms.get(platform.lower(), {})
        profile_config = platform_config.get(profile.lower())
        if not profile_config:
            return None

        token = profile_config.get("token")
        if not token:
            return None

        return PlatformCredential(
            platform=platform.lower(),
            token=token,
            profile=profile.lower(),
            source=f"file:{self.credentials_file}:{platform.lower()}/{profile.lower()}",
        )

    def _get_database_from_file(self, profile: str) -> DatabaseCredential | None:
        if self.credentials_file is None or not self.credentials_file.exists():
            return None

        payload = json.loads(self.credentials_file.read_text(encoding="utf-8-sig"))
        databases: dict[str, Any] = payload.get("databases", {})
        db_config = databases.get(profile.lower())
        if not db_config:
            return None

        required = ["host", "port", "user", "password"]
        if any(not db_config.get(key) for key in required):
            return None

        return DatabaseCredential(
            profile=profile.lower(),
            type=str(db_config.get("type", "mysql")),
            host=str(db_config["host"]),
            port=int(db_config["port"]),
            user=str(db_config["user"]),
            password=str(db_config["password"]),
            source=f"file:{self.credentials_file}:databases/{profile.lower()}",
            description=str(db_config.get("description", "")),
        )


def _build_token_env_name(platform: str, profile: str) -> str:
    if profile == "DEFAULT":
        return f"AI_PIPELINE_CREDENTIAL_{platform}_TOKEN"
    return f"AI_PIPELINE_CREDENTIAL_{platform}_{profile}_TOKEN"


def _normalize_name(value: str) -> str:
    return value.strip().replace("-", "_").upper()


def _redact_token(token: str) -> str:
    if len(token) <= 4:
        return "***"
    return f"***{token[-4:]}"
