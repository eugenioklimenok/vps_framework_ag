"""
Structured backup planning for OPERATE backup-project.
"""

from dataclasses import dataclass, field
from pathlib import Path

from models.enums import OutputDirectoryClassification


@dataclass(frozen=True)
class BackupPlan:
    """Resolved backup plan used by archive creation and validation."""

    project_root: Path
    output_dir: Path
    project_slug: str
    artifact_path: Path
    checksum_path: Path
    included_source_paths: tuple[Path, ...]
    output_dir_classification: OutputDirectoryClassification
    include_env: bool = False
    excluded_generated_paths: tuple[Path, ...] = field(default_factory=tuple)
    expected_archive_members: tuple[str, ...] = ("./project.yaml",)
