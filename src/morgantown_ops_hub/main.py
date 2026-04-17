"""CLI entry point for the Morgantown Operations Hub scaffold."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from morgantown_ops_hub import __version__
from morgantown_ops_hub.config_loader import ConfigValidationError, load_config_bundle
from morgantown_ops_hub.logging_utils import configure_logging
from morgantown_ops_hub.source_resolution import (
    ResolutionError,
    load_candidate_fixture,
    resolve_candidates,
)


def build_parser() -> argparse.ArgumentParser:
    """Create the basic command-line parser."""
    parser = argparse.ArgumentParser(description="Initialize the Morgantown Operations Hub scaffold.")
    parser.add_argument("--log-level", default="INFO", help="Console log level, such as INFO or DEBUG.")
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("config"),
        help="Directory containing sources.yaml, precedence_rules.yaml, and refresh_rules.yaml.",
    )
    parser.add_argument(
        "--candidate-fixture",
        type=Path,
        help="Optional JSON fixture of source candidate metadata for local dry-run resolution.",
    )
    parser.add_argument(
        "--dry-run-resolution",
        action="store_true",
        help="Run local source-resolution against the candidate fixture after config validation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for dry-run JSON artifacts.",
    )
    return parser


def main() -> int:
    """Validate config and optionally run a local source-resolution dry run."""
    args = build_parser().parse_args()
    logger = configure_logging(args.log_level)
    logger.info("Version: %s", __version__)

    try:
        config_bundle = load_config_bundle(args.config_dir)
        logger.info(
            "Config validation succeeded for %s sources, %s precedence domains, and %s refresh rules.",
            len(config_bundle.manifest.sources),
            len(config_bundle.precedence_rules.precedence),
            len(config_bundle.refresh_rules.rules),
        )

        if not args.dry_run_resolution:
            return 0

        if args.candidate_fixture is None:
            logger.info("Dry-run resolution requested without a fixture; config validation completed successfully.")
            return 0

        fixture = load_candidate_fixture(args.candidate_fixture)
        report = resolve_candidates(
            config_bundle.manifest.sources,
            config_bundle.manifest.exclusions,
            fixture.candidates,
            generated_at=datetime.now(timezone.utc),
            site=config_bundle.manifest.site,
            plant_scope=config_bundle.manifest.plant_scope,
            fixture_path=args.candidate_fixture,
        )

        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output_dir / "source_resolution_dry_run.json"
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(report.model_dump(mode="json"), handle, indent=2)
            handle.write("\n")

        logger.info("Dry-run source resolution completed for %s sources.", len(report.records))
        logger.info("Wrote source resolution artifact to %s", output_path)
        return 0
    except (ConfigValidationError, ResolutionError) as exc:
        logger.error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
