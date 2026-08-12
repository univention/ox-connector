# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
Find unresolved Sphinx ``:envvar:`` cross-references in generated HTML.

Sphinx renders unresolved ``:envvar:`` roles as ``code`` elements with the
``xref std std-envvar`` classes, but without wrapping them in an internal or
external reference link.

The script prints one finding per unresolved envvar reference:

    path:line:html-fragment

Exit status:

* 0: no unresolved envvar references found
* 1: unresolved envvar references found
* 2: usage or input error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENVAR_MARKER = '<code class="xref std std-envvar'


def main() -> int:
    args = parse_args()

    html_dir = args.html_dir
    if not html_dir.is_dir():
        print(f"HTML directory does not exist: {html_dir}", file=sys.stderr)
        return 2

    findings = list(find_unresolved_envvars(html_dir))

    for path, line, fragment in findings:
        print(f"{path}:{line}: {fragment}")

    return 1 if findings else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "html_dir",
        type=Path,
        help="Directory that contains generated Sphinx HTML files.",
    )
    return parser.parse_args()


def find_unresolved_envvars(html_dir: Path) -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []

    for path in sorted(html_dir.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        findings.extend(find_unresolved_envvars_in_file(path, text))

    return findings


def find_unresolved_envvars_in_file(
    path: Path,
    text: str,
) -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []
    start = 0

    while True:
        pos = text.find(ENVAR_MARKER, start)
        if pos == -1:
            break

        if not is_inside_resolved_reference(text, pos):
            line = text.count("\n", 0, pos) + 1
            fragment = get_line_fragment(text, pos)
            findings.append((path, line, fragment))

        start = pos + len(ENVAR_MARKER)

    return findings


def is_inside_resolved_reference(text: str, pos: int) -> bool:
    line_start = text.rfind("\n", 0, pos) + 1
    before = text[line_start:pos]

    last_open_link = before.rfind("<a ")
    last_close_link = before.rfind("</a>")

    if last_open_link <= last_close_link:
        return False

    link_start = before[last_open_link:]
    return (
        'class="reference internal"' in link_start
        or 'class="reference external"' in link_start
    )


def get_line_fragment(text: str, pos: int) -> str:
    line_start = text.rfind("\n", 0, pos) + 1
    line_end = text.find("\n", pos)

    if line_end == -1:
        line_end = len(text)

    return text[line_start:line_end].strip()


if __name__ == "__main__":
    sys.exit(main())
