"""
Runner for the OPERATE backup module.
"""

from datetime import datetime, timezone
from pathlib import Path
import re

from models.enums import BackupResultState, OutputDirectoryClassification
from models.operate_result import BackupResult
from modules.operate.backup.archive import create_backup_archive, validate_backup_artifact
from modules.operate.backup.paths import (
    classify_output_directory,
    ensure_output_directory,
    resolve_project_root,
)
from modules.operate.backup.plan import BackupPlan
from modules.operate.utils import validate_project_identity


def run_backup_project(
    path: str,
    output_dir: str | None = None,
    include_env: bool = False,
) -> BackupResult:
    """
    Orchestrates project backup through explicit path planning and artifact validation.
    """
    ok, target_path, reason = resolve_project_root(path)
    if not ok:
        return BackupResult(result_state=BackupResultState.BLOCKED, blocked_reason=reason)

    is_valid, slug, reason = validate_project_identity(target_path)
    if not is_valid:
        return BackupResult(result_state=BackupResultState.BLOCKED, blocked_reason=reason)

    output_inspection = classify_output_directory(output_dir or "", target_path)
    if output_inspection.classification not in (
        OutputDirectoryClassification.EXISTS_WRITABLE,
        OutputDirectoryClassification.MISSING_CREATABLE,
    ):
        return BackupResult(
            result_state=BackupResultState.BLOCKED,
            project_slug=slug,
            blocked_reason=output_inspection.reason,
        )

    created, create_reason = ensure_output_directory(output_inspection)
    if not created:
        return BackupResult(
            result_state=BackupResultState.BLOCKED,
            project_slug=slug,
            blocked_reason=create_reason,
        )

    revalidated = classify_output_directory(str(output_inspection.resolved_path), target_path)
    if revalidated.classification != OutputDirectoryClassification.EXISTS_WRITABLE:
        return BackupResult(
            result_state=BackupResultState.BLOCKED,
            project_slug=slug,
            blocked_reason=revalidated.reason or "Output directory failed post-creation validation.",
        )

    plan = build_backup_plan(
        project_root=target_path,
        output_dir=revalidated.resolved_path,
        project_slug=slug,
        output_classification=revalidated.classification,
        include_env=include_env,
    )

    success, archive_path, checksum_path, error = create_backup_archive(plan)
    if not success:
        return BackupResult(
            result_state=BackupResultState.FAILED,
            project_slug=slug,
            artifact_path=archive_path,
            checksum_path=checksum_path,
            blocked_reason=error,
            plan=plan,
        )

    artifact_valid, validation_reason = validate_backup_artifact(plan)
    if not artifact_valid:
        return BackupResult(
            result_state=BackupResultState.FAILED,
            project_slug=slug,
            artifact_path=archive_path,
            checksum_path=checksum_path,
            artifact_validated=False,
            blocked_reason=validation_reason,
            plan=plan,
        )

    return BackupResult(
        result_state=BackupResultState.CREATED,
        project_slug=slug,
        artifact_path=archive_path,
        checksum_path=checksum_path,
        artifact_validated=True,
        plan=plan,
    )


def build_backup_plan(
    project_root: Path,
    output_dir: Path,
    project_slug: str,
    output_classification: OutputDirectoryClassification,
    include_env: bool,
) -> BackupPlan:
    safe_slug = _safe_slug(project_slug)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    archive_name = f"{safe_slug}__backup__{timestamp}.tar.gz"
    artifact_path = output_dir / archive_name
    checksum_path = output_dir / f"{archive_name}.sha256"
    return BackupPlan(
        project_root=project_root,
        output_dir=output_dir,
        project_slug=project_slug,
        artifact_path=artifact_path,
        checksum_path=checksum_path,
        included_source_paths=(project_root,),
        output_dir_classification=output_classification,
        include_env=include_env,
        excluded_generated_paths=(artifact_path, checksum_path),
    )


def _safe_slug(slug: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", slug).strip(".-")
    return safe or "project"
