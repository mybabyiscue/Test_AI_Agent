from __future__ import annotations

import argparse
from pathlib import Path

from .orchestrator import run_demo_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI API testing pipeline MVP CLI")
    parser.add_argument("--run-demo", action="store_true", help="Run the built-in demo pipeline")
    parser.add_argument("--requirement", help="Requirement document path")
    parser.add_argument("--api-doc", help="Local OpenAPI/Swagger JSON/YAML path")
    parser.add_argument("--api-source-url", help="Apifox URL used to fetch API assets")
    parser.add_argument("--run-id", default="manual-run", help="Run identifier")
    parser.add_argument(
        "--workspace",
        default="workspace",
        help="Workspace directory used to store run artifacts",
    )
    parser.add_argument(
        "--agent4-excel-confirmed",
        action="store_true",
        help="Confirm Agent 4 Excel template has been reviewed",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.run_demo:
        result = run_demo_pipeline(workspace_root=Path(args.workspace))
        print(result.manifest_path)
        return

    if args.requirement:
        from .orchestrator import PipelineOrchestrator

        orchestrator = PipelineOrchestrator()
        result = orchestrator.run(
            requirement_path=Path(args.requirement),
            workspace_root=Path(args.workspace),
            run_id=args.run_id,
            api_doc_path=Path(args.api_doc) if args.api_doc else None,
            api_source_url=args.api_source_url,
            agent4_excel_confirmed=args.agent4_excel_confirmed,
        )
        print(result.manifest_path)
        return

    parser.error("No action provided. Use --run-demo or --requirement.")


if __name__ == "__main__":
    main()
