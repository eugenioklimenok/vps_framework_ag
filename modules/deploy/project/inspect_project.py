"""
Project inspection logic for the DEPLOY module.
Governed by: DEPLOY_BASELINE_TDD.md §9 and DEPLOY_PROJECT_SPEC.md §8
"""

from pathlib import Path
from typing import Optional

from models.enums import DeploymentClassification


def extract_project_slug(project_yaml_path: Path) -> Optional[str]:
    """
    Naively extract project_slug from project.yaml.
    In a real app we might use PyYAML, but to keep dependencies low
    we can parse the deterministic scaffold format line by line.
    """
    if not project_yaml_path.exists():
        return None

    try:
        content = project_yaml_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("project_slug:"):
                # E.g., 'project_slug: my-app'
                return line.split(":", 1)[1].strip()
        return None
    except Exception:
        return None


def inspect_project_for_deployment(target_path: Path) -> tuple[DeploymentClassification, str, str]:
    """
    Inspects a project root and classifies its deployability.

    Returns:
        Tuple of (classification, project_slug, blocked_reason)
    """
    if not target_path.exists() or not target_path.is_dir():
        return DeploymentClassification.BLOCKED, "", "Project path does not exist or is not a directory."

    project_yaml = target_path / "project.yaml"
    compose_yaml = target_path / "compose.yaml"

    if not project_yaml.exists():
        return DeploymentClassification.BLOCKED, "", "Missing authoritative project.yaml metadata."

    if not compose_yaml.exists():
        return DeploymentClassification.BLOCKED, "", "Missing baseline compose.yaml definition."

    slug = extract_project_slug(project_yaml)
    if not slug:
        return DeploymentClassification.BLOCKED, "", "project.yaml is malformed or missing project_slug."

    # In the current baseline, if it has the required files and valid metadata,
    # it is considered READY for deploy configuration validation.
    # Note: REDEPLOYABLE state will be decided by runtime wrappers checking
    # if services are already up, but for the filesystem inspect, READY is the base success state.
    
    return DeploymentClassification.READY, slug, ""
