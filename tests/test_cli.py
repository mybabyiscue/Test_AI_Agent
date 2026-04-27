from __future__ import annotations

from ai_pipeline.cli import build_parser


def test_cli_accepts_apifox_source_url_mode():
    args = build_parser().parse_args(
        [
            "--requirement",
            "examples/requirements/sample_requirement.md",
            "--api-source-url",
            "https://app.apifox.com/project/123456/api-789",
            "--workspace",
            "workspace",
            "--run-id",
            "apifox-run",
        ]
    )

    assert args.requirement == "examples/requirements/sample_requirement.md"
    assert args.api_source_url == "https://app.apifox.com/project/123456/api-789"
    assert args.run_id == "apifox-run"
