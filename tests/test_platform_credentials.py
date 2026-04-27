from __future__ import annotations

import json

import pytest

from ai_pipeline.credentials import CredentialNotFoundError, EnvCredentialProvider


def test_env_credential_provider_reads_platform_token_without_exposing_raw_secret(monkeypatch):
    monkeypatch.setenv("AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN", "secret-token")

    provider = EnvCredentialProvider(credentials_file=None)
    credential = provider.get("apifox")

    assert credential.platform == "apifox"
    assert credential.token == "secret-token"
    assert credential.redacted() == {
        "platform": "apifox",
        "profile": "default",
        "token": "***oken",
        "source": "env:AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN",
    }


def test_env_credential_provider_keeps_platform_profiles_isolated(monkeypatch):
    monkeypatch.setenv("AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN", "default-token")
    monkeypatch.setenv("AI_PIPELINE_CREDENTIAL_APIFOX_TEAM_A_TOKEN", "team-a-token")

    provider = EnvCredentialProvider(credentials_file=None)

    assert provider.get("apifox").token == "default-token"
    assert provider.get("apifox", profile="team_a").token == "team-a-token"


def test_env_credential_provider_raises_when_token_missing(monkeypatch):
    monkeypatch.delenv("AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN", raising=False)

    provider = EnvCredentialProvider(credentials_file=None)

    with pytest.raises(CredentialNotFoundError):
        provider.get("apifox")


def test_credential_provider_reads_local_management_file_without_env_var(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PIPELINE_CREDENTIAL_APIFOX_TOKEN", raising=False)
    credentials_file = tmp_path / "credentials.local.json"
    credentials_file.write_text(
        json.dumps(
            {
                "platforms": {
                    "apifox": {
                        "default": {"token": "file-token"},
                        "team_a": {"token": "team-file-token"},
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    provider = EnvCredentialProvider(credentials_file=credentials_file)

    credential = provider.get("apifox")
    team_credential = provider.get("apifox", profile="team_a")

    assert credential.token == "file-token"
    assert credential.source.endswith("credentials.local.json:apifox/default")
    assert team_credential.token == "team-file-token"
