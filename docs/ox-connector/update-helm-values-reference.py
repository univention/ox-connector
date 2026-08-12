# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Update the OX Connector Helm Chart values reference.

Run from the repository root in the Sphinx base container image.

Generate from the published user-facing Helm Chart::

    python3 docs/ox-connector/update-helm-values-reference.py 0.42.1

Alternatively, set the version through the environment::

    OX_CONNECTOR_HELM_VERSION=0.42.1 \
        python3 docs/ox-connector/update-helm-values-reference.py

Generate from the local chart in this repository::

    python3 docs/ox-connector/update-helm-values-reference.py --local
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHART_NAME = "ox-connector"
CHART_REPOSITORY = (
    "oci://artifacts.software-univention.de/nubus/charts/ox-connector"
)
LOCAL_CHART_DIR = Path("helm/ox-connector")
OUTPUT_FILE = Path(
    "docs/ox-connector/configuration/reference-values-kubernetes.txt",
)
FRIGATE_TEMPLATE = Path("docs/ox-connector/.frigate")


def main() -> int:
    args = parse_args()
    validate_repository_root()

    chart_dir: Path
    tmpdir: tempfile.TemporaryDirectory[str] | None = None

    try:
        if args.local:
            chart_dir = get_local_chart_dir()
        else:
            chart_version = args.chart_version or os.environ.get(
                "OX_CONNECTOR_HELM_VERSION",
            )
            if not chart_version:
                print_usage_error()
                return 2
            tmpdir = tempfile.TemporaryDirectory()
            chart_dir = pull_chart(chart_version, Path(tmpdir.name))

        generated = generate_reference(chart_dir)
        validate_reference(
            generated,
            args.local,
            args.chart_version or os.environ.get("OX_CONNECTOR_HELM_VERSION"),
        )
        OUTPUT_FILE.write_text(generated, encoding="utf-8")

        if args.local:
            print(f"Updated {OUTPUT_FILE} from local chart {chart_dir}")
        else:
            print(
                f"Updated {OUTPUT_FILE} for OX Connector Helm Chart version "
                f"{args.chart_version or os.environ.get('OX_CONNECTOR_HELM_VERSION')}",
            )

        return 0
    except FileNotFoundError as exc:
        print(f"Required command not found: {exc.filename}", file=sys.stderr)
        return 127
    except subprocess.CalledProcessError as exc:
        print(
            f"Command failed with exit code {exc.returncode}: {' '.join(exc.cmd)}",
            file=sys.stderr,
        )
        return exc.returncode
    finally:
        remove_frigate_link(locals().get("chart_dir"))
        if tmpdir is not None:
            tmpdir.cleanup()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "chart_version",
        nargs="?",
        help="Published OX Connector Helm Chart version to document.",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Generate the reference from helm/ox-connector instead of the published chart.",
    )
    args = parser.parse_args()

    if args.local and args.chart_version:
        parser.error("--local doesn't accept a chart version")

    return args


def validate_repository_root() -> None:
    if not FRIGATE_TEMPLATE.is_file() or not OUTPUT_FILE.parent.is_dir():
        raise SystemExit("Run this script from the repository root.")


def get_local_chart_dir() -> Path:
    if (
        not (LOCAL_CHART_DIR / "Chart.yaml").is_file()
        or not (LOCAL_CHART_DIR / "values.yaml").is_file()
    ):
        raise SystemExit(f"Local chart not found: {LOCAL_CHART_DIR}")
    return LOCAL_CHART_DIR


def pull_chart(chart_version: str, tmpdir: Path) -> Path:
    run(
        [
            "helm",
            "pull",
            CHART_REPOSITORY,
            "--version",
            chart_version,
            "--destination",
            str(tmpdir),
        ],
    )

    archive = tmpdir / f"{CHART_NAME}-{chart_version}.tgz"
    if not archive.is_file():
        raise SystemExit(f"Downloaded chart archive not found: {archive}")

    shutil.unpack_archive(str(archive), tmpdir)

    chart_dir = tmpdir / CHART_NAME
    if not chart_dir.is_dir():
        raise SystemExit(f"Extracted chart directory not found: {chart_dir}")

    return chart_dir


def generate_reference(chart_dir: Path) -> str:
    chart_frigate = chart_dir / ".frigate"
    if chart_frigate.is_symlink() or chart_frigate.exists():
        chart_frigate.unlink()
    chart_frigate.symlink_to(Path.cwd() / FRIGATE_TEMPLATE)

    result = run(
        [
            "frigate",
            "gen",
            "--output-format",
            "rst",
            "--no-credits",
            "--helm-docs",
            "--skip-helm-update",
            str(chart_dir),
        ],
        capture_output=True,
    )
    return result.stdout


def validate_reference(
    generated: str,
    local: bool,
    chart_version: str | None,
) -> None:
    if local:
        expected = f":Name: ``{CHART_NAME}``"
        error = f"Generated reference does not contain expected chart name: {CHART_NAME}"
    else:
        expected = f":Version: ``{chart_version}``"
        error = f"Generated reference does not contain expected version: {chart_version}"

    if expected not in generated:
        raise SystemExit(error)


def remove_frigate_link(chart_dir: object) -> None:
    if not isinstance(chart_dir, Path):
        return

    chart_frigate = chart_dir / ".frigate"
    if chart_frigate.is_symlink() or chart_frigate.exists():
        chart_frigate.unlink()


def print_usage_error() -> None:
    print(
        "Usage: update-helm-values-reference.py <OX_CONNECTOR_HELM_VERSION>",
        file=sys.stderr,
    )
    print(
        "Or set OX_CONNECTOR_HELM_VERSION in the environment.",
        file=sys.stderr,
    )
    print(
        "Or use --local to generate from helm/ox-connector.",
        file=sys.stderr,
    )


def run(
    args: list[str],
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture_output else None,
    )


if __name__ == "__main__":
    sys.exit(main())
