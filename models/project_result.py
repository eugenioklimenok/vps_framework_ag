"""
Project execution result models.
"""

from dataclasses import dataclass, field
from pathlib import Path

from models.enums import ScaffoldAction, TargetClassification


@dataclass(frozen=True)
class ScaffoldResult:
    """Result of a new-project execution.
    
    Attributes:
        classification:   Final target path classification before mutation.
        actions_taken:    List of actions performed.
        created_paths:    List of paths created (directories and files).
        reused_paths:     List of paths safely reused.
        blocked_reason:   Reason for aborting, if applicable.
        validation_passed: Whether the final post-action validation passed.
    """

    classification: TargetClassification
    actions_taken: list[ScaffoldAction] = field(default_factory=list)
    created_paths: list[Path] = field(default_factory=list)
    reused_paths: list[Path] = field(default_factory=list)
    blocked_reason: str = ""
    validation_passed: bool = False
