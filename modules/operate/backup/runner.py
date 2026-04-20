"""
Runner for the OPERATE backup module.
"""

from pathlib import Path

from models.enums import BackupResultState
from models.operate_result import BackupResult
from modules.operate.backup.archive import create_backup_archive
from modules.operate.utils import validate_project_identity


def run_backup_project(path: str, include_env: bool = False) -> BackupResult:
    """
    Orchestrates the project backup.
    """
    target_path = Path(path).resolve()
    
    # Validate identity
    is_valid, slug, reason = validate_project_identity(target_path)
    if not is_valid:
        return BackupResult(
            result_state=BackupResultState.BLOCKED,
            blocked_reason=reason
        )

    # Create artifact
    success, archive_path, checksum_path, error = create_backup_archive(target_path, slug, include_env)
    
    if not success:
        return BackupResult(
            result_state=BackupResultState.FAILED,
            project_slug=slug,
            blocked_reason=error
        )
        
    return BackupResult(
        result_state=BackupResultState.CREATED,
        project_slug=slug,
        artifact_path=archive_path,
        checksum_path=checksum_path,
        artifact_validated=True
    )
