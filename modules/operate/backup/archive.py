"""
Backup artifact builder and validator for the OPERATE module.
"""

import hashlib
import tarfile
from pathlib import Path

from modules.operate.backup.paths import is_relative_to_path
from modules.operate.backup.plan import BackupPlan


def _generate_checksum(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def create_backup_archive(plan: BackupPlan) -> tuple[bool, Path, Path, str]:
    """
    Creates a .tar.gz backup using only the structured backup plan.
    """
    try:
        if plan.artifact_path.exists() or plan.checksum_path.exists():
            return False, plan.artifact_path, plan.checksum_path, "Backup artifact already exists."

        def _filter_tarinfo(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
            name = tarinfo.name.replace("\\", "/")
            parts = set(name.split("/"))
            if ".git" in parts or "__pycache__" in parts:
                return None
            if not plan.include_env and Path(name).name == ".env":
                return None
            return tarinfo

        with tarfile.open(plan.artifact_path, "w:gz") as tar:
            for source_path in plan.included_source_paths:
                if source_path == plan.project_root:
                    tar.add(source_path, arcname=".", filter=_filter_tarinfo)
                else:
                    tar.add(source_path, arcname=source_path.name, filter=_filter_tarinfo)

        checksum = _generate_checksum(plan.artifact_path)
        plan.checksum_path.write_text(f"{checksum} *{plan.artifact_path.name}\n", encoding="utf-8")
        return True, plan.artifact_path, plan.checksum_path, ""
    except Exception as exc:
        return False, plan.artifact_path, plan.checksum_path, f"Failed to create backup archive: {exc}"


def validate_backup_artifact(plan: BackupPlan) -> tuple[bool, str]:
    artifact = plan.artifact_path
    checksum = plan.checksum_path

    if not artifact.exists():
        return False, "Backup artifact does not exist."
    if not artifact.is_file():
        return False, "Backup artifact is not a regular file."
    try:
        resolved_artifact = artifact.resolve(strict=True)
        resolved_output = plan.output_dir.resolve(strict=True)
    except Exception as exc:
        return False, f"Backup artifact path could not be resolved: {exc}"
    if resolved_artifact != plan.artifact_path:
        return False, "Backup artifact path does not match the backup plan."
    if not is_relative_to_path(resolved_artifact, resolved_output):
        return False, "Backup artifact is not under the planned output directory."
    if artifact.stat().st_size == 0:
        return False, "Backup artifact is empty."
    if not tarfile.is_tarfile(artifact):
        return False, "Backup artifact is not readable as an archive."

    try:
        with tarfile.open(artifact, "r:gz") as tar:
            names = set(tar.getnames())
            tar.getmembers()
    except Exception as exc:
        return False, f"Backup artifact is not readable as an archive: {exc}"

    for expected_member in plan.expected_archive_members:
        if expected_member not in names:
            return False, f"Backup artifact is missing expected content: {expected_member}"

    forbidden_names = {artifact.name, checksum.name}
    for member_name in names:
        normalized = member_name.replace("\\", "/")
        if Path(normalized).name in forbidden_names:
            return False, "Backup artifact includes generated artifact or checksum sidecar."

    if not checksum.exists():
        return False, "Backup checksum sidecar does not exist."
    if not checksum.is_file():
        return False, "Backup checksum sidecar is not a regular file."
    checksum_text = checksum.read_text(encoding="utf-8").strip()
    if not checksum_text:
        return False, "Backup checksum sidecar is empty."
    actual_checksum = _generate_checksum(artifact)
    if actual_checksum not in checksum_text or artifact.name not in checksum_text:
        return False, "Backup checksum sidecar does not match the artifact."

    return True, ""
