"""PDF report metadata persistence for Milestone 4."""

from datetime import datetime, timezone
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from database.connection import get_database
from database.milestone4_models import ReportMetadataRecord


async def _validate_report_relationships(
    report: ReportMetadataRecord,
) -> None:
    """Validate referenced roadmap and summary versions."""

    database = get_database()

    if report.roadmap_id is not None:
        roadmap_query: dict[str, Any] = {
            "workspace_id": report.workspace_id,
            "roadmap_id": report.roadmap_id,
        }

        if report.roadmap_version is not None:
            roadmap_query["version"] = report.roadmap_version
        else:
            roadmap_query["is_current"] = True

        roadmap = await database.roadmaps.find_one(
            roadmap_query,
            {"_id": 1},
        )

        if roadmap is None:
            raise ValueError(
                "The referenced roadmap does not exist "
                "in this workspace."
            )

    if report.summary_id is not None:
        summary_query: dict[str, Any] = {
            "workspace_id": report.workspace_id,
            "summary_id": report.summary_id,
        }

        if report.summary_version is not None:
            summary_query["version"] = report.summary_version
        else:
            summary_query["is_current"] = True

        summary = await database.executive_summaries.find_one(
            summary_query,
            {"_id": 1},
        )

        if summary is None:
            raise ValueError(
                "The referenced executive summary does not "
                "exist in this workspace."
            )


async def create_report_metadata(
    report: ReportMetadataRecord | dict[str, Any],
) -> dict[str, Any]:
    """Create metadata for a requested PDF report."""

    database = get_database()

    report_model = (
        report
        if isinstance(report, ReportMetadataRecord)
        else ReportMetadataRecord.model_validate(report)
    )

    await _validate_report_relationships(report_model)

    document = report_model.model_dump(mode="python")
    await database.report_metadata.insert_one(document)

    return document


async def get_report_metadata(
    workspace_id: str,
    report_id: str,
) -> dict[str, Any] | None:
    """Retrieve one report while enforcing workspace isolation."""

    database = get_database()

    return await database.report_metadata.find_one(
        {
            "workspace_id": workspace_id,
            "report_id": report_id,
        }
    )


async def mark_report_generating(
    workspace_id: str,
    report_id: str,
) -> dict[str, Any] | None:
    """Mark a queued report as being generated."""

    database = get_database()

    return await database.report_metadata.find_one_and_update(
        {
            "workspace_id": workspace_id,
            "report_id": report_id,
            "generation_status": "queued",
        },
        {
            "$set": {
                "generation_status": "generating",
                "error_message": None,
            }
        },
        return_document=ReturnDocument.AFTER,
    )


async def complete_report(
    workspace_id: str,
    report_id: str,
    file_name: str,
    storage_key: str,
    file_size_bytes: int,
    content_hash: str,
    download_url: str | None = None,
) -> dict[str, Any] | None:
    """Store successful PDF generation metadata."""

    database = get_database()

    if file_size_bytes < 0:
        raise ValueError(
            "Report file size cannot be negative."
        )

    return await database.report_metadata.find_one_and_update(
        {
            "workspace_id": workspace_id,
            "report_id": report_id,
        },
        {
            "$set": {
                "generation_status": "completed",
                "file_name": file_name,
                "storage_key": storage_key,
                "download_url": download_url,
                "mime_type": "application/pdf",
                "file_size_bytes": file_size_bytes,
                "content_hash": content_hash,
                "generated_at": datetime.now(timezone.utc),
                "error_message": None,
            }
        },
        return_document=ReturnDocument.AFTER,
    )


async def fail_report(
    workspace_id: str,
    report_id: str,
    error_message: str,
) -> dict[str, Any] | None:
    """Record a PDF generation failure."""

    database = get_database()

    return await database.report_metadata.find_one_and_update(
        {
            "workspace_id": workspace_id,
            "report_id": report_id,
        },
        {
            "$set": {
                "generation_status": "failed",
                "error_message": error_message,
                "generated_at": datetime.now(timezone.utc),
            }
        },
        return_document=ReturnDocument.AFTER,
    )


async def list_workspace_reports(
    workspace_id: str,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List report metadata for one workspace."""

    database = get_database()

    query: dict[str, Any] = {
        "workspace_id": workspace_id,
    }

    if status is not None:
        query["generation_status"] = status

    safe_limit = max(1, min(limit, 100))

    cursor = (
        database.report_metadata
        .find(query)
        .sort("requested_at", DESCENDING)
        .limit(safe_limit)
    )

    return [document async for document in cursor]
