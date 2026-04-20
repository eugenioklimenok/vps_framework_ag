"""
Shared utilities for OPERATE module.
Governed by: OPERATE_BASELINE_TDD.md
"""

from pathlib import Path
from typing import Optional


def extract_project_slug(project_yaml_path: Path) -> Optional[str]:
    """
    Extracts the project_slug from project.yaml.
    Duplicated from DEPLOY to keep modules decoupled as per strict domain boundaries,
    but can be moved to a shared utils/project.py if explicitly allowed.
    For now, strict separation is maintained.
    """
    if not project_yaml_path.exists():
        return None

    try:
        content = project_yaml_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("project_slug:"):
                return line.split(":", 1)[1].strip()
        return None
    except Exception:
        return None


def validate_project_identity(target_path: Path) -> tuple[bool, str, str]:
    """
    Validates that a path is a valid project scaffold.
    Returns: (is_valid, slug, error_reason)
    """
    if not target_path.exists() or not target_path.is_dir():
        return False, "", "Project path does not exist or is not a directory."

    project_yaml = target_path / "project.yaml"
    if not project_yaml.exists():
        return False, "", "Missing authoritative project.yaml metadata."

    slug = extract_project_slug(project_yaml)
    if not slug:
        return False, "", "project.yaml is malformed or missing project_slug."

    return True, slug, ""
