"""
Target inspection and classification for the PROJECT module.

Governed by: PROJECT_BASELINE_TDD.md §9 and PROJECT_BASELINE_CONTRACT.md §7
"""

from pathlib import Path
from models.enums import TargetClassification
from config.project_config import REQUIRED_PROJECT_DIRS, REQUIRED_PROJECT_FILES


def classify_target(target_path: Path, expected_slug: str = None) -> TargetClassification:
    """
    Inspects a target directory and classifies its state for scaffolding.

    Classification logic:
        - CLEAN: Path does not exist or is completely empty.
        - COMPATIBLE: Path contains exactly the framework scaffold structure
                      (meaning it's an existing project we can safely re-run on).
        - SANEABLE: Path exists and has some files, but no framework scaffold collisions.
                    (e.g., an empty git repo, or just a README).
        - BLOCKED: Path exists and contains conflicting non-framework files or a
                   broken/partial scaffold that cannot be trusted.
    """
    if not target_path.exists():
        return TargetClassification.CLEAN

    if not target_path.is_dir():
        # A file exists where we want to put a directory.
        return TargetClassification.BLOCKED

    # Check if directory is empty
    children = list(target_path.iterdir())
    if not children:
        return TargetClassification.CLEAN

    # Check if it looks like a compatible framework project
    has_project_yaml = (target_path / "project.yaml").exists()
    has_compose_yaml = (target_path / "compose.yaml").exists()

    if has_project_yaml:
        if expected_slug:
            try:
                content = (target_path / "project.yaml").read_text(encoding="utf-8")
                slug_match = False
                for line in content.splitlines():
                    if line.startswith("project_slug:"):
                        yaml_slug = line.split(":", 1)[1].strip()
                        yaml_slug = yaml_slug.strip("'\" ")
                        if yaml_slug == expected_slug:
                            slug_match = True
                        break
                
                if not slug_match:
                    return TargetClassification.BLOCKED
            except Exception:
                return TargetClassification.BLOCKED

    if has_project_yaml and has_compose_yaml:
        # We assume if it has the core identity files, it's our project.
        # It's safe to run new-project again over it (idempotency).
        return TargetClassification.COMPATIBLE

    if has_project_yaml or has_compose_yaml:
        # Partial framework state - dangerous to overwrite or guess
        return TargetClassification.BLOCKED

    # It's an existing directory without framework files.
    # We only allow it if it looks "saneable" (e.g. only .git, README.md).
    # If it has lots of arbitrary files, we block to prevent destructive overwriting.
    allowed_saneable_files = {".git", "README.md", ".gitignore"}
    for child in children:
        if child.name not in allowed_saneable_files:
            return TargetClassification.BLOCKED

    return TargetClassification.SANEABLE
