# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH
"""Per-job request-ID ContextVar for lancelog's ``request_id_func``.

Used by the ``consumer`` to attribute log records to
the ``object`` currently being processed.
"""

from contextvars import ContextVar


REQUEST_ID_SENTINEL = "-"
"""Value used when no job is in flight. Matches lancelog's own ``"-"`` default
so idle/poll log lines render as ``[         -]``."""


_job_id_var: ContextVar[str] = ContextVar(
    "job_id",
    default=REQUEST_ID_SENTINEL,
)


get_job_id = _job_id_var.get
"""Bound directly as ``request_id_func`` on ``setup_logging``."""


def set_job_id(value: str | None) -> None:
    """Set the current job id; pass ``None`` or ``""`` to reset to the sentinel."""
    _job_id_var.set(value if value else REQUEST_ID_SENTINEL)
