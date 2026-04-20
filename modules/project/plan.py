"""
Project generation business logic.
"""

from pathlib import Path

from models.enums import ScaffoldAction, TargetClassification
from models.project_result import ScaffoldResult
from modules.project.inspect_target import classify_target


def validate_slug(slug: str) -> bool:
    """
    Validates a project slug according to NEW_PROJECT_SPEC.md rules.
    Must be lowercase, alphanumeric, and hyphens only.
    """
    if not slug:
        return False
    import re

    return bool(re.match(r"^[a-z0-9-]+$", slug))


def plan_scaffold(target_path: Path) -> ScaffoldResult:
    """
    Evaluates the target path and returns a plan based on its classification.
    No mutation happens here.
    """
    classification = classify_target(target_path)

    if classification == TargetClassification.BLOCKED:
        return ScaffoldResult(
            classification=classification,
            actions_taken=[ScaffoldAction.BLOCK],
            blocked_reason=f"Target path '{target_path}' contains conflicting or ambiguous files.",
        )

    # In a real plan, we don't return the full result yet, but we determine 
    # what actions will be taken. Since ScaffoldResult is our final return,
    # the actual creation logic will build the final result.
    
    # We return an intermediate blocked result if something is wrong.
    # Otherwise we return a 'clean' base result that will be populated by the materializer.
    return ScaffoldResult(classification=classification)
