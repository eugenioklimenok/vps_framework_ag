"""
Path resolution and output directory classification for backup-project.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from models.enums import OutputDirectoryClassification


@dataclass(frozen=True)
class OutputDirectoryInspection:
    classification: OutputDirectoryClassification
    resolved_path: Path
    reason: str = ""


def is_relative_to_path(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_project_root(raw_path: str) -> tuple[bool, Path, str]:
    if not raw_path:
        return False, Path(), "Missing required project path."
    try:
        project_root = Path(raw_path).expanduser().resolve(strict=True)
    except Exception as exc:
        return False, Path(), f"Project path could not be resolved: {exc}"
    if not project_root.is_dir():
        return False, project_root, "Project path does not exist or is not a directory."
    return True, project_root, ""


def classify_output_directory(raw_output_dir: str, project_root: Path) -> OutputDirectoryInspection:
    if not raw_output_dir:
        return OutputDirectoryInspection(
            OutputDirectoryClassification.INVALID,
            Path(),
            "Missing required output directory.",
        )

    try:
        requested = Path(raw_output_dir).expanduser()
        if requested.exists():
            resolved = requested.resolve(strict=True)
            if not resolved.is_dir():
                return OutputDirectoryInspection(
                    OutputDirectoryClassification.INVALID,
                    resolved,
                    "Output path exists but is not a directory.",
                )
            if _is_inside_or_equal(resolved, project_root):
                return OutputDirectoryInspection(
                    OutputDirectoryClassification.UNSAFE,
                    resolved,
                    "Output directory resolves inside project root.",
                )
            if not os.access(resolved, os.W_OK):
                return OutputDirectoryInspection(
                    OutputDirectoryClassification.INVALID,
                    resolved,
                    "Output directory is not writable.",
                )
            return OutputDirectoryInspection(
                OutputDirectoryClassification.EXISTS_WRITABLE,
                resolved,
            )

        parent = requested.parent if requested.parent != Path("") else Path(".")
        if not parent.exists():
            return OutputDirectoryInspection(
                OutputDirectoryClassification.INVALID,
                requested.resolve(strict=False),
                "Output directory parent does not exist.",
            )
        parent_resolved = parent.resolve(strict=True)
        if not parent_resolved.is_dir():
            return OutputDirectoryInspection(
                OutputDirectoryClassification.INVALID,
                parent_resolved,
                "Output directory parent is not a directory.",
            )
        candidate = (parent_resolved / requested.name).resolve(strict=False)
        if _is_inside_or_equal(candidate, project_root):
            return OutputDirectoryInspection(
                OutputDirectoryClassification.UNSAFE,
                candidate,
                "Output directory resolves inside project root.",
            )
        if not os.access(parent_resolved, os.W_OK):
            return OutputDirectoryInspection(
                OutputDirectoryClassification.INVALID,
                candidate,
                "Output directory parent is not writable.",
            )
        return OutputDirectoryInspection(
            OutputDirectoryClassification.MISSING_CREATABLE,
            candidate,
        )
    except OSError as exc:
        return OutputDirectoryInspection(
            OutputDirectoryClassification.AMBIGUOUS,
            Path(raw_output_dir),
            f"Output directory resolution is ambiguous: {exc}",
        )
    except Exception as exc:
        return OutputDirectoryInspection(
            OutputDirectoryClassification.INVALID,
            Path(raw_output_dir),
            f"Output directory could not be resolved: {exc}",
        )


def ensure_output_directory(inspection: OutputDirectoryInspection) -> tuple[bool, str]:
    if inspection.classification == OutputDirectoryClassification.EXISTS_WRITABLE:
        return True, ""
    if inspection.classification != OutputDirectoryClassification.MISSING_CREATABLE:
        return False, inspection.reason
    try:
        inspection.resolved_path.mkdir()
    except Exception as exc:
        return False, f"Output directory could not be created: {exc}"
    return True, ""


def _is_inside_or_equal(candidate: Path, project_root: Path) -> bool:
    return candidate == project_root or is_relative_to_path(candidate, project_root)
