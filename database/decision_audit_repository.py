from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID, uuid4

from bson import ObjectId
from pymongo import DESCENDING

from database.connection import get_database


DecisionEntityType = Literal[
    "roadmap",
    "executive_summary",
]


ENTITY_CONFIGURATION: dict[str, dict[str, str]] = {
    "roadmap": {
        "collection": "roadmaps",
        "id_field": "roadmap_id",
    },
    "executive_summary": {
        "collection": "executive_summaries",
        "id_field": "summary_id",
    },
}


# These fields are expected to change as part of normal system
# operation and are excluded from the approved-content hash.
EXCLUDED_CONTENT_FIELDS = {
    "_id",
    "is_current",
    "quality_metrics",
}


def _normalize_datetime(value: datetime) -> str:
    """Convert a datetime to a consistent UTC representation."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    value = value.astimezone(timezone.utc)

    # MongoDB stores datetime values with millisecond precision.
    value = value.replace(
        microsecond=(value.microsecond // 1000) * 1000
    )

    return value.isoformat(timespec="milliseconds").replace(
        "+00:00",
        "Z",
    )


def _normalize_for_hash(value: Any) -> Any:
    """Convert MongoDB values into deterministic JSON values."""

    if isinstance(value, dict):
        return {
            str(key): _normalize_for_hash(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0]),
            )
            if key not in EXCLUDED_CONTENT_FIELDS
        }

    if isinstance(value, (list, tuple)):
        return [
            _normalize_for_hash(item)
            for item in value
        ]

    if isinstance(value, set):
        normalized_items = [
            _normalize_for_hash(item)
            for item in value
        ]

        return sorted(
            normalized_items,
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                default=str,
            ),
        )

    if isinstance(value, datetime):
        return _normalize_datetime(value)

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, bytes):
        return value.hex()

    return value


def _calculate_hash(payload: Any) -> str:
    """Calculate a deterministic SHA-256 hash."""

    normalized_payload = _normalize_for_hash(payload)

    canonical_json = json.dumps(
        normalized_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


def _build_chain_payload(
    *,
    workspace_id: str,
    entity_type: DecisionEntityType,
    entity_id: str,
    version: int,
    content_hash: str,
    previous_hash: str | None,
    approved_by: str,
    approved_at: datetime,
) -> dict[str, Any]:
    """Build the metadata protected by the hash chain."""

    return {
        "workspace_id": workspace_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "version": version,
        "content_hash": content_hash,
        "previous_hash": previous_hash,
        "approved_by": approved_by,
        "approved_at": approved_at,
    }


def _get_entity_configuration(
    entity_type: DecisionEntityType,
) -> dict[str, str]:
    """Return the MongoDB configuration for an entity type."""

    configuration = ENTITY_CONFIGURATION.get(entity_type)

    if configuration is None:
        raise ValueError(
            f"Unsupported decision entity type: {entity_type}"
        )

    return configuration


async def create_decision_audit(
    *,
    workspace_id: str,
    entity_type: DecisionEntityType,
    entity_id: str,
    version: int,
    approved_by: str | None = None,
) -> dict[str, Any]:
    """
    Create an immutable audit record for an approved document.

    The content hash protects the approved document fields.
    The chain hash links the record with the previous approved
    version of the same entity.
    """

    if version < 1:
        raise ValueError("Version must be at least 1.")

    database = get_database()
    configuration = _get_entity_configuration(entity_type)

    collection = database[
        configuration["collection"]
    ]
    id_field = configuration["id_field"]

    source_document = await collection.find_one(
        {
            "workspace_id": workspace_id,
            id_field: entity_id,
            "version": version,
        }
    )

    if source_document is None:
        raise ValueError(
            f"{entity_type} version was not found in this "
            "workspace."
        )

    if source_document.get("review_status") != "approved":
        raise ValueError(
            "Only an approved document can receive a "
            "decision audit record."
        )

    existing_audit = await database.decision_audits.find_one(
        {
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version": version,
        }
    )

    if existing_audit is not None:
        verification = await verify_decision_integrity(
            workspace_id=workspace_id,
            entity_type=entity_type,
            entity_id=entity_id,
            version=version,
        )

        if not verification["verified"]:
            raise ValueError(
                "An audit record already exists, but the "
                "approved document no longer matches it."
            )

        return existing_audit

    approval_user = (
        approved_by
        or source_document.get("approved_by")
    )

    if not approval_user:
        raise ValueError(
            "approved_by is required to create an audit record."
        )

    approval_time = source_document.get("approved_at")

    if not isinstance(approval_time, datetime):
        approval_time = datetime.now(timezone.utc)
    elif approval_time.tzinfo is None:
        # PyMongo may return MongoDB UTC dates without tzinfo.
        approval_time = approval_time.replace(
            tzinfo=timezone.utc
        )

    approval_time = approval_time.astimezone(
        timezone.utc
    ).replace(
        microsecond=(
            approval_time.microsecond // 1000
        )
        * 1000
    )

    previous_audit = await database.decision_audits.find_one(
        {
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version": {
                "$lt": version,
            },
        },
        sort=[
            ("version", DESCENDING),
        ],
    )

    previous_hash = (
        previous_audit.get("chain_hash")
        if previous_audit is not None
        else None
    )

    content_hash = _calculate_hash(source_document)

    chain_payload = _build_chain_payload(
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id,
        version=version,
        content_hash=content_hash,
        previous_hash=previous_hash,
        approved_by=approval_user,
        approved_at=approval_time,
    )

    chain_hash = _calculate_hash(chain_payload)

    created_at = datetime.now(timezone.utc)
    created_at = created_at.replace(
        microsecond=(created_at.microsecond // 1000) * 1000
    )

    audit_document = {
        "audit_id": str(uuid4()),
        "workspace_id": workspace_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "version": version,
        "algorithm": "SHA-256",
        "content_hash": content_hash,
        "previous_hash": previous_hash,
        "chain_hash": chain_hash,
        "approved_by": approval_user,
        "approved_at": approval_time,
        "created_at": created_at,
    }

    audit_document = {
        "audit_id": str(uuid4()),
        "workspace_id": workspace_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "version": version,
        "algorithm": "SHA-256",
        "content_hash": content_hash,
        "previous_hash": previous_hash,
        "chain_hash": chain_hash,
        "approved_by": approval_user,
        "approved_at": approval_time,
        "created_at": created_at,
    }

    await database.decision_audits.insert_one(
        audit_document
    )

    return audit_document


async def verify_decision_integrity(
    *,
    workspace_id: str,
    entity_type: DecisionEntityType,
    entity_id: str,
    version: int,
) -> dict[str, Any]:
    """
    Verify approved content, chain metadata, and previous link.

    A false result indicates that the document or its audit
    chain no longer matches the originally recorded values.
    """

    database = get_database()
    configuration = _get_entity_configuration(entity_type)

    collection = database[
        configuration["collection"]
    ]
    id_field = configuration["id_field"]

    source_document = await collection.find_one(
        {
            "workspace_id": workspace_id,
            id_field: entity_id,
            "version": version,
        }
    )

    audit_document = await database.decision_audits.find_one(
        {
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version": version,
        }
    )

    if source_document is None or audit_document is None:
        return {
            "verified": False,
            "content_matches": False,
            "chain_matches": False,
            "previous_link_matches": False,
            "reason": (
                "The source document or audit record "
                "was not found."
            ),
        }

    current_content_hash = _calculate_hash(
        source_document
    )

    content_matches = (
        current_content_hash
        == audit_document.get("content_hash")
    )

    chain_payload = _build_chain_payload(
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id,
        version=version,
        content_hash=audit_document["content_hash"],
        previous_hash=audit_document.get(
            "previous_hash"
        ),
        approved_by=audit_document["approved_by"],
        approved_at=audit_document["approved_at"],
    )

    expected_chain_hash = _calculate_hash(
        chain_payload
    )

    chain_matches = (
        expected_chain_hash
        == audit_document.get("chain_hash")
    )

    previous_audit = await database.decision_audits.find_one(
        {
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version": {
                "$lt": version,
            },
        },
        sort=[
            ("version", DESCENDING),
        ],
    )

    expected_previous_hash = (
        previous_audit.get("chain_hash")
        if previous_audit is not None
        else None
    )

    previous_link_matches = (
        audit_document.get("previous_hash")
        == expected_previous_hash
    )

    verified = (
        content_matches
        and chain_matches
        and previous_link_matches
    )

    return {
        "verified": verified,
        "content_matches": content_matches,
        "chain_matches": chain_matches,
        "previous_link_matches": (
            previous_link_matches
        ),
        "entity_type": entity_type,
        "entity_id": entity_id,
        "version": version,
        "audit_id": audit_document.get(
            "audit_id"
        ),
        "algorithm": audit_document.get(
            "algorithm"
        ),
        "reason": (
            "Approved decision integrity verified."
            if verified
            else (
                "The approved document or audit chain "
                "has changed."
            )
        ),
    }


async def get_decision_audit(
    *,
    workspace_id: str,
    entity_type: DecisionEntityType,
    entity_id: str,
    version: int,
) -> dict[str, Any] | None:
    """Retrieve one workspace-scoped audit record."""

    database = get_database()

    return await database.decision_audits.find_one(
        {
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version": version,
        }
    )