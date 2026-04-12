"""
In-memory mock persistence for the Barangay Record Request demo.
Data resets when the development server process exits.
"""
from __future__ import annotations

import itertools
import threading
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_lock = threading.Lock()
_counter = itertools.count(1)
REQUESTS: list[dict[str, Any]] = []

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_READY = "ready"

DOCUMENT_LABELS = {
    "clearance": "Barangay Clearance",
    "health": "Health Certification",
    "indigency": "Certificate of Indigency",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_reference() -> str:
    return f"REF-{uuid4().hex[:8].upper()}"


def add_request(
    *,
    document_type: str,
    full_name: str,
    address: str,
    purpose: str,
    contact: str,
    bhw_officer: str,
) -> dict[str, Any]:
    with _lock:
        ref = _generate_reference()
        while any(r["reference"] == ref for r in REQUESTS):
            ref = _generate_reference()
        record = {
            "id": next(_counter),
            "reference": ref,
            "document_type": document_type,
            "status": STATUS_PENDING,
            "full_name": full_name.strip(),
            "address": address.strip(),
            "purpose": purpose.strip(),
            "contact": contact.strip(),
            "bhw_officer": bhw_officer.strip(),
            "created_at": _now_iso(),
        }
        REQUESTS.insert(0, record)
        return record.copy()


def list_requests() -> list[dict[str, Any]]:
    with _lock:
        return [r.copy() for r in REQUESTS]


def get_by_reference(reference: str) -> dict[str, Any] | None:
    ref = (reference or "").strip().upper()
    with _lock:
        for r in REQUESTS:
            if r["reference"].upper() == ref:
                return r.copy()
    return None


def set_status(record_id: int, status: str) -> bool:
    with _lock:
        for r in REQUESTS:
            if r["id"] == record_id:
                r["status"] = status
                return True
    return False


def delete_all() -> int:
    with _lock:
        n = len(REQUESTS)
        REQUESTS.clear()
        return n
